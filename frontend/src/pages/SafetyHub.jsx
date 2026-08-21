import React, { useState, useEffect } from 'react';
import { BookOpen, Lightbulb, CheckCircle } from 'lucide-react';
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
      } catch (e) {}
    };
    const fetchQuiz = async () => {
      try {
        const res = await api.get('/learn/quiz');
        setQuizQuestions(res.data.questions || []);
      } catch (e) {}
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
    } catch (e) {}
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-extrabold text-white flex items-center gap-3">
          <BookOpen className="w-8 h-8 text-amber-400" />
          Cyber Safety Hub
        </h1>
        <p className="text-slate-300 text-sm">
          Daily tips, threat awareness articles, and interactive cybersecurity quizzes to keep you protected.
        </p>
      </div>

      {/* Daily Tip Highlight Card */}
      {dailyTip && (
        <div className="p-6 rounded-2xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 space-y-2">
          <div className="flex items-center gap-2 text-amber-400 font-semibold text-xs uppercase tracking-wider">
            <Lightbulb className="w-4 h-4" />
            Daily Safety Tip — {dailyTip.date}
          </div>
          <p className="text-white text-base font-medium leading-relaxed">{dailyTip.tip_text}</p>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-border">
        <button
          onClick={() => setActiveTab('tips')}
          className={`px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'tips' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Daily Tips
        </button>
        <button
          onClick={() => setActiveTab('quiz')}
          className={`px-5 py-3 text-sm font-semibold border-b-2 transition-all ${
            activeTab === 'quiz' ? 'border-amber-400 text-amber-400' : 'border-transparent text-slate-400 hover:text-white'
          }`}
        >
          Cybersecurity Quiz
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'quiz' && (
        <div className="space-y-6">
          {!user && (
            <p className="text-sm text-slate-400">
              <Link to="/login" className="text-primary font-semibold hover:underline">Log in</Link> to take the cybersecurity quiz.
            </p>
          )}
          {quizQuestions.map((q, idx) => (
            <div key={q.question_id} className="p-6 rounded-2xl bg-surface border border-border space-y-4">
              <h3 className="text-base font-bold text-white flex items-start gap-2">
                <span className="text-amber-400 font-extrabold">{idx + 1}.</span>
                {q.question_text}
              </h3>
              <div className="space-y-2">
                {q.options.map((opt) => (
                  <button
                    key={opt.option_id}
                    onClick={() => handleAnswerSubmit(q.question_id, opt.option_id)}
                    className="w-full text-left p-3.5 rounded-xl bg-background border border-border hover:border-amber-400/50 text-slate-200 text-sm transition-colors"
                  >
                    {opt.text}
                  </button>
                ))}
              </div>

              {quizAnswers[q.question_id] && (
                <div className={`p-4 rounded-xl border text-sm space-y-1 ${
                  quizAnswers[q.question_id].is_correct
                    ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                    : 'bg-red-500/10 border-red-500/30 text-red-300'
                }`}>
                  <strong className="block font-semibold">
                    {quizAnswers[q.question_id].is_correct ? 'Correct!' : 'Incorrect!'}
                  </strong>
                  <p>{quizAnswers[q.question_id].explanation}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
