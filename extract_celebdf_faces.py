import os
import cv2
import random
import time
from PIL import Image

def process_video(video_path, output_dir, split_name, label, prefix, face_cascade, num_frames=5):
    if not os.path.exists(video_path):
        return 0
        
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        cap.release()
        return 0

    step = max(1, total_frames // (num_frames + 1))
    extracted_count = 0
    
    for i in range(num_frames):
        frame_idx = (i + 1) * step
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50))
        
        if len(faces) > 0:
            # Take largest face
            faces = sorted(faces, key=lambda b: b[2]*b[3], reverse=True)
            x, y, w, h = faces[0]
            # Add padding
            h_pad, w_pad = int(h * 0.15), int(w * 0.15)
            y1, y2 = max(0, y - h_pad), min(frame.shape[0], y + h + h_pad)
            x1, x2 = max(0, x - w_pad), min(frame.shape[1], x + w + w_pad)
            crop = frame[y1:y2, x1:x2]
        else:
            # Fallback to center crop if no face detected by cascade
            h_f, w_f, _ = frame.shape
            ch, cw = int(h_f * 0.6), int(w_f * 0.6)
            y1, x1 = (h_f - ch) // 2, (w_f - cw) // 2
            crop = frame[y1:y1+ch, x1:x1+cw]
            
        if crop.size == 0:
            continue
            
        crop_rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
        crop_pil = Image.fromarray(crop_rgb).resize((224, 224), Image.BILINEAR)
        
        out_filename = f"{prefix}_frame_{i}.jpg"
        out_filepath = os.path.join(output_dir, split_name, label, out_filename)
        crop_pil.save(out_filepath, quality=95)
        extracted_count += 1
        
    cap.release()
    return extracted_count

def run_extraction():
    celeb_dir = r"D:\dataset\Celeb-DF"
    target_dir = r"D:\dataset\Celeb-DF-cropped"
    
    test_txt = os.path.join(celeb_dir, "List_of_testing_videos.txt")
    with open(test_txt, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    test_map = {}
    for line in lines:
        parts = line.split()
        if len(parts) == 2:
            lbl, rel_path = parts[0], parts[1].replace('/', os.sep)
            test_map[rel_path] = "real" if lbl == "1" else "fake"

    all_real = []
    for sub in ["Celeb-real", "YouTube-real"]:
        p = os.path.join(celeb_dir, sub)
        for f in os.listdir(p):
            if f.endswith(".mp4"):
                all_real.append(os.path.join(sub, f))

    all_fake = []
    p = os.path.join(celeb_dir, "Celeb-synthesis")
    for f in os.listdir(p):
        if f.endswith(".mp4"):
            all_fake.append(os.path.join("Celeb-synthesis", f))

    rem_real = [v for v in all_real if v not in test_map]
    rem_fake = [v for v in all_fake if v not in test_map]

    random.seed(42)
    random.shuffle(rem_real)
    random.shuffle(rem_fake)

    val_real_cnt = int(len(rem_real) * 0.2)
    val_fake_cnt = int(len(rem_fake) * 0.2)

    val_real = rem_real[:val_real_cnt]
    train_real = rem_real[val_real_cnt:]

    val_fake = rem_fake[:val_fake_cnt]
    train_fake = rem_fake[val_fake_cnt:]

    splits = {
        "train": {"real": train_real, "fake": train_fake},
        "val": {"real": val_real, "fake": val_fake},
        "test": {"real": [v for v in test_map if test_map[v] == "real"],
                 "fake": [v for v in test_map if test_map[v] == "fake"]}
    }

    for split in ["train", "val", "test"]:
        for lbl in ["real", "fake"]:
            os.makedirs(os.path.join(target_dir, split, lbl), exist_ok=True)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    t0 = time.time()
    
    print("Starting Celeb-DF Face Extraction into", target_dir, "...")
    stats = {}
    for split_name, categories in splits.items():
        stats[split_name] = {"real": 0, "fake": 0}
        for lbl, vid_list in categories.items():
            print(f"Extracting {split_name}/{lbl} ({len(vid_list)} videos)...")
            count = 0
            for idx, vid_rel in enumerate(vid_list):
                vid_path = os.path.join(celeb_dir, vid_rel)
                prefix = f"{lbl}_{idx}_{os.path.splitext(os.path.basename(vid_rel))[0]}"
                extracted = process_video(vid_path, target_dir, split_name, lbl, prefix, face_cascade, num_frames=5)
                count += extracted
            stats[split_name][lbl] = count

    print(f"Face extraction complete in {time.time() - t0:.2f}s")
    print("Final Extracted Image Counts:")
    for split_name, counts in stats.items():
        print(f"  {split_name}: Real={counts['real']}, Fake={counts['fake']}, Total={counts['real']+counts['fake']}")

if __name__ == "__main__":
    run_extraction()
