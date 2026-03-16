import { useEffect, useState } from 'react';
import { CalendarDays, RefreshCw } from 'lucide-react';
import { api } from '../lib/api';
import type { DayPlan } from '../types/api';

const MEAL_COLORS: Record<string, string> = {
  breakfast: 'bg-amber-50 border-amber-200 text-amber-800',
  lunch: 'bg-sky-50 border-sky-200 text-sky-800',
  dinner: 'bg-forest-50 border-forest-200 text-forest-800',
};

export default function MealPlan() {
  const [week, setWeek] = useState<DayPlan[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getMealPlan();
      setWeek(data.week ?? []);
    } catch {
      setError('Could not load meal plan. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-stone-800 flex items-center gap-2">
            <CalendarDays className="text-forest-600" /> Weekly Meal Plan
          </h1>
          <p className="text-stone-500 mt-1">AI-generated balanced meals for every day of the week.</p>
        </div>
        <button onClick={load} className="flex items-center gap-2 text-sm text-stone-600 hover:text-forest-700 border border-stone-200 hover:border-forest-300 px-4 py-2 rounded-xl transition-colors">
          <RefreshCw size={14} /> Regenerate
        </button>
      </div>

      {error && <div className="bg-red-50 text-red-600 rounded-xl p-4 mb-6">{error}</div>}

      {loading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {Array.from({ length: 7 }).map((_, i) => (
            <div key={i} className="bg-white rounded-2xl p-4 border border-stone-100 animate-pulse">
              <div className="h-4 bg-stone-200 rounded w-1/2 mb-4" />
              {[0, 1, 2].map((j) => <div key={j} className="h-10 bg-stone-100 rounded-xl mb-2" />)}
            </div>
          ))}
        </div>
      ) : week.length === 0 ? (
        <div className="text-center py-20 text-stone-400">No meal plan available.</div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {week.map((day) => (
            <div key={day.day} className="bg-white rounded-2xl p-4 border border-stone-100 shadow-sm">
              <h2 className="font-semibold text-stone-700 mb-3">{day.day}</h2>
              <div className="space-y-2">
                {day.meals.map((slot) => (
                  <div key={slot.meal_type} className={`rounded-xl border px-3 py-2 text-xs ${MEAL_COLORS[slot.meal_type] ?? 'bg-stone-50 border-stone-200 text-stone-700'}`}>
                    <div className="font-medium capitalize mb-0.5">{slot.meal_type}</div>
                    <div className="opacity-80">{slot.recipe?.name ?? '—'}</div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
