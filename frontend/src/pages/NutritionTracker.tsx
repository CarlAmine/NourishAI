import { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { BarChart3 } from 'lucide-react';
import { api } from '../lib/api';
import type { NutritionDay, NutritionInfo } from '../types/api';

const MACRO_COLORS = ['#4ade80', '#60a5fa', '#f59e0b', '#f87171'];

export default function NutritionTracker() {
  const [days, setDays] = useState<NutritionDay[]>([]);
  const [averages, setAverages] = useState<NutritionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getNutrition()
      .then((data) => {
        setDays(data.days ?? []);
        setAverages(data.averages ?? null);
      })
      .catch(() => setError('Could not load nutrition data.'))
      .finally(() => setLoading(false));
  }, []);

  const pieData = averages
    ? [
        { name: 'Protein', value: averages.protein ?? 0 },
        { name: 'Carbs', value: averages.carbs ?? 0 },
        { name: 'Fat', value: averages.fat ?? 0 },
        { name: 'Fiber', value: averages.fiber ?? 0 },
      ].filter((d) => d.value > 0)
    : [];

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10">
        <div className="h-8 bg-stone-200 rounded w-48 mb-8 animate-pulse" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[0, 1, 2].map((i) => <div key={i} className="bg-white rounded-2xl h-64 border border-stone-100 animate-pulse" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-3xl font-bold text-stone-800 flex items-center gap-2 mb-2">
        <BarChart3 className="text-forest-600" /> Nutrition Tracker
      </h1>
      <p className="text-stone-500 mb-8">Daily macro breakdown and trends.</p>

      {error && <div className="bg-red-50 text-red-600 rounded-xl p-4 mb-6">{error}</div>}

      {averages && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Avg Calories', value: averages.calories, unit: 'kcal', color: 'bg-amber-50 text-amber-700' },
            { label: 'Avg Protein', value: averages.protein, unit: 'g', color: 'bg-forest-50 text-forest-700' },
            { label: 'Avg Carbs', value: averages.carbs, unit: 'g', color: 'bg-sky-50 text-sky-700' },
            { label: 'Avg Fat', value: averages.fat, unit: 'g', color: 'bg-rose-50 text-rose-700' },
          ].map(({ label, value, unit, color }) => (
            <div key={label} className={`rounded-2xl p-4 ${color}`}>
              <div className="text-2xl font-bold">{value ?? '—'}<span className="text-sm font-normal ml-1">{unit}</span></div>
              <div className="text-sm opacity-75 mt-1">{label}</div>
            </div>
          ))}
        </div>
      )}

      {days.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
            <h2 className="font-semibold text-stone-700 mb-4">Calories Over Time</h2>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={days}>
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="calories" stroke="#f59e0b" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
            <h2 className="font-semibold text-stone-700 mb-4">Macros by Day</h2>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={days}>
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="protein" fill="#4ade80" />
                <Bar dataKey="carbs" fill="#60a5fa" />
                <Bar dataKey="fat" fill="#f87171" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {pieData.length > 0 && (
            <div className="bg-white rounded-2xl border border-stone-100 shadow-sm p-5">
              <h2 className="font-semibold text-stone-700 mb-4">Average Macro Split</h2>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {pieData.map((_, i) => <Cell key={i} fill={MACRO_COLORS[i % MACRO_COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      )}

      {days.length === 0 && !error && (
        <div className="text-center py-20 text-stone-400">No nutrition data available yet.</div>
      )}
    </div>
  );
}
