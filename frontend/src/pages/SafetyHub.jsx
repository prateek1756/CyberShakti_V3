import React, { useState, useEffect } from 'react';
import { BookOpen, Lightbulb, CheckCircle2, ShieldCheck, HelpCircle } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

export const SafetyHub = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('tips');
  const [dailyTip, setDailyTip] = useState(null);
  const [quizQuestions, setQuizQuestions] = useState([]);
  const [quizAnswers, setQuizAnswers] = useState({});

  useEffect(() => {
    const fetchTip = async () => {
      try {
        const res = await api.get('/learn/daily-tip');
        setDailyTip(res.data);
      } catch {
        // Handled silently
      }
    };
    const fetchQuiz = async () => {
      try {
        const res = await api.get('/learn/quiz');
        setQuizQuestions(res.data.questions || []);
      } catch {
        // Handled silently
      }
    };
    fetchTip();
    fetchQuiz();
  }, []);

  const handleAnswerSubmit = async (qId, optionId) => {
    try {
      const res = await api.post('/learn/quiz/submit-answer', {
        question_id: qId,
        selected_option_id: optionId,
      });
      setQuizAnswers((prev) => ({ ...prev, [qId]: res.data }));
    } catch {
      // Handled silently
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-bold">
          <BookOpen className="w-3.5 h-3.5" /> THREAT AWARENESS & PREVENTION
        </div>
        <h1 className="text-3xl sm:text-4xl font-display font-extrabold text-white tracking-tight flex items-center gap-3">
          Cyber Safety Hub
        </h1>
        <p className="text-slate-300 text-sm max-w-xl">
          Daily threat tips, educational guides, and interactive cybersecurity quizzes to protect you against digital fraud.
        </p>
      </div>

      {/* Daily Tip Highlight Card */}
      {dailyTip && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-950/40 via-surface to-surface border border-amber-500/30 space-y-3 shadow-xl">
          <div className="flex items-center gap-2 text-amber-400 font-mono font-bold text-xs uppercase tracking-wider">
            <Lightbulb className="w-4 h-4" />
            DAILY SAFETY TIP — {dailyTip.date}
          </div>
          <p className="text-white text-base font-medium leading-relaxed">{dailyTip.tip_text}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex p-1 rounded-xl bg-surface border border-border max-w-md">
        <button
          onClick={() => setActiveTab('tips')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'tips'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <Lightbulb className="w-3.5 h-3.5" />
          Safety Guidance
        </button>
        <button
          onClick={() => setActiveTab('quiz')}
          className={`flex-1 py-2.5 px-4 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-2 ${
            activeTab === 'quiz'
              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-md'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <HelpCircle className="w-3.5 h-3.5" />
          Interactive Quiz
        </button>
      </div>

      {/* Quiz Tab */}
      {activeTab === 'quiz' && (
        <div className="space-y-6">
          {!user && (
            <p className="text-xs text-slate-400">
              <Link to="/login" className="text-cyan-400 font-bold hover:underline">Log in</Link> to save your quiz answers and build your profile score.
            </p>
          )}

          {quizQuestions.map((q, idx) => (
            <div key={q.question_id} className="p-6 rounded-2xl bg-surface border border-border space-y-4 shadow-lg">
              <h3 className="text-sm sm:text-base font-display font-bold text-white flex items-start gap-3">
                <span className="text-amber-400 font-mono font-bold text-lg">{idx + 1}.</span>
                {q.question_text}
              </h3>
              <div className="space-y-2.5">
                {q.options.map((opt) => (
                  <button
                    key={opt.option_id}
                    onClick={() => handleAnswerSubmit(q.question_id, opt.option_id)}
                    className="w-full text-left p-4 rounded-xl bg-background/80 border border-border hover:border-amber-400/50 text-slate-200 text-xs font-medium transition-all"
                  >
                    {opt.text}
                  </button>
                ))}
              </div>

              {quizAnswers[q.question_id] && (
                <div className={`p-4 rounded-xl border text-xs space-y-1 ${
                  quizAnswers[q.question_id].is_correct
                    ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                    : 'bg-red-950/40 border-red-500/40 text-red-300'
                }`}>
                  <strong className="block font-bold text-sm">
                    {quizAnswers[q.question_id].is_correct ? '✓ Correct Answer' : '⚠ Incorrect'}
                  </strong>
                  <p className="text-slate-200 leading-relaxed">{quizAnswers[q.question_id].explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
