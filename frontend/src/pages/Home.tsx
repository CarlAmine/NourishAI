import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Sparkles, CalendarDays, BarChart3, CheckCircle, XCircle } from 'lucide-react';
import { api } from '../lib/api';

const features = [
  {
    to: '/search',
    icon: Search,
    title: 'Recipe Search',
    description: 'Semantic search across thousands of recipes with smart filters and reranking.',
    color: 'bg-sky-50 text-sky-600',
  },
  {
    to: '/recommend',
    icon: Sparkles,
    title: 'AI Recommender',
    description: 'Tell us what ingredients you have and get personalized recipe suggestions.',
    color: 'bg-violet-50 text-violet-600',
  },
  {
    to: '/meal-plan',
    icon: CalendarDays,
    title: 'Meal Planner',
    description: 'AI-generated weekly meal plans with balanced nutrition across every day.',
    color: 'bg-amber-50 text-amber-600',
  },
  {
    to: '/nutrition',
    icon: BarChart3,
    title: 'Nutrition Tracker',
    description: 'Track daily macros and visualize your nutritional trends over time.',
    color: 'bg-forest-50 text-forest-600',
  },
];

export default function Home() {
  const [health, setHealth] = useState<'loading' | 'ok' | 'error'>('loading');

  useEffect(() => {
    api.health()
      .then(() => setHealth('ok'))
      .catch(() => setHealth('error'));
  }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-12">
      {/* Hero */}
      <div className="text-center mb-14">
        <div className="inline-flex items-center gap-2 bg-forest-50 text-forest-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          {health === 'loading' && <span className="w-2 h-2 bg-amber-400 rounded-full animate-pulse" />}
          {health === 'ok' && <CheckCircle size={14} />}
          {health === 'error' && <XCircle size={14} className="text-red-500" />}
          {health === 'loading' ? 'Connecting to backend…' : health === 'ok' ? 'Backend online' : 'Backend offline'}
        </div>
        <h1 className="text-5xl font-bold text-stone-800 mb-4">
          Eat smarter with{' '}
          <span className="text-forest-600">NourishAI</span>
        </h1>
        <p className="text-xl text-stone-500 max-w-2xl mx-auto">
          AI-powered nutrition and recipe recommendations tailored to your ingredients, goals, and taste.
        </p>
        <div className="flex gap-3 justify-center mt-8">
          <Link
            to="/search"
            className="bg-forest-600 hover:bg-forest-700 text-white px-6 py-3 rounded-xl font-medium transition-colors"
          >
            Search Recipes
          </Link>
          <Link
            to="/recommend"
            className="bg-white hover:bg-stone-50 text-stone-700 border border-stone-200 px-6 py-3 rounded-xl font-medium transition-colors"
          >
            Get Recommendations
          </Link>
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
        {features.map(({ to, icon: Icon, title, description, color }) => (
          <Link
            key={to}
            to={to}
            className="group bg-white rounded-2xl p-6 border border-stone-100 shadow-sm hover:shadow-md hover:border-forest-200 transition-all"
          >
            <div className={`inline-flex p-3 rounded-xl mb-4 ${color}`}>
              <Icon size={22} />
            </div>
            <h2 className="font-semibold text-stone-800 group-hover:text-forest-700 transition-colors mb-1">
              {title}
            </h2>
            <p className="text-sm text-stone-500">{description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
