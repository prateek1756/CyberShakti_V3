"""
F-06 EfficientNet-B4 Deepfake Detector — Real Training on Celeb-DF
===================================================================
- Dataset: Celeb-DF (real Celeb-DF.zip, extracted + face-cropped)
- Architecture: EfficientNet-B4 (PyTorch / torchvision)
- Transfer Learning: ImageNet-pretrained weights
- Output: Binary classifier (0=fake, 1=real)
- Conformant with ADR-010, CSHAKTI-ML-001 §7.4
"""

import os
import json
import time
import random
import logging

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms
from torchvision.models import efficientnet_b4, EfficientNet_B4_Weights
from PIL import Image
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                              f1_score, confusion_matrix, roc_auc_score)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────
DATA_DIR        = r"D:\dataset\Celeb-DF-cropped"
OUTPUT_CKPT     = r"D:\dataset\Celeb-DF-cropped\best_f06_efficientnet_b4.pth"
METRICS_FILE    = os.path.join("ml", "models", "f06_efficientnet_metrics.json")

BATCH_SIZE      = 16
EPOCHS          = 10
LR              = 2e-4
LR_STEP         = 4
LR_GAMMA        = 0.5
RANDOM_SEED     = 42
PATIENCE        = 3    # early stopping patience
IMG_SIZE        = 224
NUM_CLASSES     = 2

# ─────────────────────────────────────────────────────────
# Reproducibility
# ─────────────────────────────────────────────────────────
random.seed(RANDOM_SEED)
torch.manual_seed(RANDOM_SEED)

# ─────────────────────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────────────────────
class DeepfakeFrameDataset(Dataset):
    """Loads face-cropped JPEG frames. Label: 0=fake, 1=real"""
    def __init__(self, root_dir, split, transform=None):
        self.samples = []
        self.transform = transform
        label_map = {"real": 1, "fake": 0}
        for lbl, idx in label_map.items():
            folder = os.path.join(root_dir, split, lbl)
            if not os.path.exists(folder):
                continue
            for fname in os.listdir(folder):
                if fname.lower().endswith((".jpg", ".jpeg", ".png")):
                    self.samples.append((os.path.join(folder, fname), idx))
        # Shuffle for training reproducibility
        random.shuffle(self.samples)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


# ─────────────────────────────────────────────────────────
# Transforms (ImageNet stats)
# ─────────────────────────────────────────────────────────
train_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.1),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])

eval_tf = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
])


# ─────────────────────────────────────────────────────────
# Model
# ─────────────────────────────────────────────────────────
class DeepfakeEfficientNetDetector(nn.Module):
    """EfficientNet-B4 binary classifier per ADR-010 & CSHAKTI-ML-001 §7.4."""
    def __init__(self, pretrained=True):
        super().__init__()
        weights = EfficientNet_B4_Weights.DEFAULT if pretrained else None
        self.backbone = efficientnet_b4(weights=weights)
        num_ftrs = self.backbone.classifier[1].in_features
        self.backbone.classifier = nn.Sequential(
            nn.Dropout(p=0.3, inplace=True),
            nn.Linear(num_ftrs, NUM_CLASSES),
        )

    def forward(self, x):
        return self.backbone(x)


# ─────────────────────────────────────────────────────────
# Training loop
# ─────────────────────────────────────────────────────────
def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, count = 0.0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(labels)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        count += len(labels)
    return total_loss / count, correct / count


@torch.no_grad()
def eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss, correct, count = 0.0, 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        outputs = model(imgs)
        loss = criterion(outputs, labels)
        total_loss += loss.item() * len(labels)
        correct += (outputs.argmax(dim=1) == labels).sum().item()
        count += len(labels)
    return total_loss / count, correct / count


@torch.no_grad()
def evaluate_test(model, loader, device):
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    for imgs, labels in loader:
        imgs = imgs.to(device)
        outputs = model(imgs)
        probs = torch.softmax(outputs, dim=1)[:, 1].cpu().tolist()
        preds = outputs.argmax(dim=1).cpu().tolist()
        all_probs.extend(probs)
        all_preds.extend(preds)
        all_labels.extend(labels.tolist())
    return all_labels, all_preds, all_probs


# ─────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────
def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info("Device: %s", device)

    # Datasets
    train_ds = DeepfakeFrameDataset(DATA_DIR, "train", train_tf)
    val_ds   = DeepfakeFrameDataset(DATA_DIR, "val",   eval_tf)
    test_ds  = DeepfakeFrameDataset(DATA_DIR, "test",  eval_tf)

    logger.info("Train samples: %d | Val: %d | Test: %d",
                len(train_ds), len(val_ds), len(test_ds))

    if len(train_ds) == 0 or len(val_ds) == 0 or len(test_ds) == 0:
        raise RuntimeError("One or more dataset splits are empty. Check extraction.")

    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=0, pin_memory=False)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=0, pin_memory=False)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=0, pin_memory=False)

    # Model
    model = DeepfakeEfficientNetDetector(pretrained=True).to(device)

    # Class weights for imbalanced data
    n_real = sum(1 for _, l in train_ds.samples if l == 1)
    n_fake = sum(1 for _, l in train_ds.samples if l == 0)
    total  = n_real + n_fake
    w_real = total / (2 * n_real) if n_real else 1.0
    w_fake = total / (2 * n_fake) if n_fake else 1.0
    class_weights = torch.tensor([w_fake, w_real], dtype=torch.float).to(device)
    logger.info("Class weights — fake: %.4f, real: %.4f", w_fake, w_real)

    criterion = nn.CrossEntropyLoss(weight=class_weights)
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=LR_STEP, gamma=LR_GAMMA)

    best_val_acc   = 0.0
    epochs_no_impr = 0
    training_log   = []
    t_start        = time.time()

    logger.info("Starting training for up to %d epochs (patience=%d)...", EPOCHS, PATIENCE)

    for epoch in range(1, EPOCHS + 1):
        t_ep = time.time()
        tr_loss, tr_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        va_loss, va_acc = eval_epoch(model, val_loader,   criterion, device)
        scheduler.step()
        ep_time = time.time() - t_ep

        logger.info("Epoch %2d/%d | tr_loss=%.4f tr_acc=%.4f | val_loss=%.4f val_acc=%.4f | %.1fs",
                    epoch, EPOCHS, tr_loss, tr_acc, va_loss, va_acc, ep_time)
        training_log.append(dict(epoch=epoch, tr_loss=round(tr_loss,4),
                                  tr_acc=round(tr_acc,4), val_loss=round(va_loss,4),
                                  val_acc=round(va_acc,4)))

        if va_acc > best_val_acc:
            best_val_acc = va_acc
            torch.save(model.state_dict(), OUTPUT_CKPT)
            logger.info("  ✓ New best val_acc=%.4f — checkpoint saved.", best_val_acc)
            epochs_no_impr = 0
        else:
            epochs_no_impr += 1
            if epochs_no_impr >= PATIENCE:
                logger.info("Early stopping at epoch %d (no improvement for %d epochs).",
                            epoch, PATIENCE)
                break

    total_time = time.time() - t_start
    logger.info("Training complete. Total time: %.1fs. Best val_acc: %.4f",
                total_time, best_val_acc)

    # ─── Load best checkpoint for evaluation ───
    logger.info("Loading best checkpoint from %s", OUTPUT_CKPT)
    model.load_state_dict(torch.load(OUTPUT_CKPT, weights_only=True))

    # ─── Test evaluation ───
    logger.info("Evaluating on held-out TEST set (%d samples)...", len(test_ds))
    labels, preds, probs = evaluate_test(model, test_loader, device)

    accuracy  = accuracy_score(labels, preds)
    precision = precision_score(labels, preds, zero_division=0)
    recall    = recall_score(labels, preds, zero_division=0)
    f1        = f1_score(labels, preds, zero_division=0)
    cm        = confusion_matrix(labels, preds).tolist()
    try:
        auc = roc_auc_score(labels, probs)
    except Exception:
        auc = None

    logger.info("Test Accuracy : %.4f", accuracy)
    logger.info("Test Precision: %.4f", precision)
    logger.info("Test Recall   : %.4f", recall)
    logger.info("Test F1       : %.4f", f1)
    logger.info("Test AUC      : %s", f"{auc:.4f}" if auc else "N/A")
    logger.info("Confusion Matrix: %s", cm)

    # ─── Save model artifacts ───
    FINAL_MODEL_PATH_1 = os.path.join("ml", "models", "f06_efficientnet_b4.pth")
    FINAL_MODEL_PATH_2 = os.path.join("backend", "app", "ml", "models", "f06_efficientnet_b4.pth")
    for p in [FINAL_MODEL_PATH_1, FINAL_MODEL_PATH_2]:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        torch.save(model.state_dict(), p)
        logger.info("Model saved to %s (%.2f MB)", p, os.path.getsize(p) / 1e6)

    metrics = {
        "dataset": "Celeb-DF (real video dataset)",
        "train_samples": len(train_ds),
        "val_samples": len(val_ds),
        "test_samples": len(test_ds),
        "epochs_trained": len(training_log),
        "best_val_accuracy": round(best_val_acc, 4),
        "test_accuracy":  round(accuracy,  4),
        "test_precision": round(precision, 4),
        "test_recall":    round(recall,    4),
        "test_f1_score":  round(f1,        4),
        "test_auc":       round(auc, 4) if auc else None,
        "confusion_matrix": cm,
        "architecture": "EfficientNet-B4",
        "framework": "PyTorch",
        "training_log": training_log,
        "random_seed": RANDOM_SEED,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "learning_rate": LR,
        "optimizer": "AdamW",
        "scheduler": f"StepLR(step={LR_STEP}, gamma={LR_GAMMA})",
        "device": str(device),
        "training_duration_seconds": round(total_time, 1),
        "artifact_paths": [FINAL_MODEL_PATH_1, FINAL_MODEL_PATH_2],
    }

    os.makedirs(os.path.dirname(METRICS_FILE), exist_ok=True)
    with open(METRICS_FILE, "w") as fh:
        json.dump(metrics, fh, indent=2)
    logger.info("Metrics saved to %s", METRICS_FILE)
    logger.info("F-06 EfficientNet-B4 training and evaluation complete.")
    return metrics


if __name__ == "__main__":
    main()
