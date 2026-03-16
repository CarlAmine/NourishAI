import { useEffect, useState } from 'react'
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { BarChart3, AlertCircle, Loader } from 'lucide-react'
import { api } from '@/lib/api'
import { NutritionData } from '@/types/api'

export function NutritionTracker() {
  const [nutritionData, setNutritionData] = useState<NutritionData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api.getNutritionData()
      .then((response) => setNutritionData(response.data || []))
      .catch((err) => setError(err instanceof Error ? err.message : 'Failed to load nutrition data'))
      .finally(() => setLoading(false))
  }, [])

  const todayData = nutritionData.length > 0 ? nutritionData[0] : null
  const todaySummary = todayData ? { calories: todayData.total_calories, protein: todayData.total_protein, carbs: todayData.total_carbs, fat: todayData.total_fat } : null

  const chartData = nutritionData.map((data) => ({
    date: new Date(data.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    calories: data.total_calories, protein: data.total_protein, carbs: data.total_carbs, fat: data.total_fat,
  }))

  const macroData = todaySummary ? [
    { name: 'Protein', value: todaySummary.protein, color: '#3D6B3A' },
    { name: 'Carbs', value: todaySummary.carbs, color: '#E07B54' },
    { name: 'Fat', value: todaySummary.fat, color: '#C8603A' },
  ] : []

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-12">
          <h1 className="font-display text-4xl font-bold text-charcoal-900 mb-3 flex items-center gap-3">
            <BarChart3 className="text-forest-600" /> Nutrition Tracker
          </h1>
          <p className="text-lg text-charcoal-700/70">Monitor your daily nutrition with detailed macro breakdowns and trends.</p>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-terracotta-50 border border-terracotta-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-terracotta-600 flex-shrink-0 mt-0.5" />
            <div><h3 className="font-medium text-terracotta-900">Error</h3><p className="text-sm text-terracotta-800 mt-1">{error}</p></div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader className="w-8 h-8 text-forest-500 mx-auto mb-4 animate-spin" />
              <p className="text-charcoal-700">Loading nutrition data...</p>
            </div>
          </div>
        )}

        {!loading && (
          <>
            {todaySummary && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                {[
                  { label: 'Calories', value: todaySummary.calories, unit: 'kcal', color: 'from-terracotta-500 to-terracotta-600', icon: '🔥' },
                  { label: 'Protein', value: todaySummary.protein, unit: 'g', color: 'from-forest-500 to-forest-600', icon: '💪' },
                  { label: 'Carbs', value: todaySummary.carbs, unit: 'g', color: 'from-terracotta-400 to-terracotta-500', icon: '🌾' },
                  { label: 'Fat', value: todaySummary.fat, unit: 'g', color: 'from-cream-300 to-cream-400', icon: '🧈' },
                ].map(({ label, value, unit, color, icon }) => (
                  <div key={label} className={`card p-6 bg-gradient-to-br ${color} text-white overflow-hidden relative`}>
                    <div className="absolute top-0 right-0 text-4xl opacity-10 -mr-2 -mt-2">{icon}</div>
                    <div className="relative z-10">
                      <p className="text-sm font-mono font-medium opacity-90 uppercase">{label}</p>
                      <p className="text-3xl font-bold mt-2">{Math.round(value)}<span className="text-lg ml-1">{unit}</span></p>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {chartData.length > 0 && (
              <div className="space-y-8">
                <div className="card p-8">
                  <h2 className="font-display text-xl font-bold text-charcoal-900 mb-6">Calorie Intake Trend</h2>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F2E4C4" />
                      <XAxis dataKey="date" stroke="#2C2C2C" />
                      <YAxis stroke="#2C2C2C" />
                      <Tooltip contentStyle={{ backgroundColor: '#FDFAF4', border: '1px solid #F2E4C4', borderRadius: '8px' }} />
                      <Legend />
                      <Line type="monotone" dataKey="calories" stroke="#C8603A" strokeWidth={2} dot={{ fill: '#C8603A', r: 4 }} activeDot={{ r: 6 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div className="card p-8">
                    <h2 className="font-display text-xl font-bold text-charcoal-900 mb-6">Daily Macros</h2>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={chartData.slice(-7)}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#F2E4C4" />
                        <XAxis dataKey="date" stroke="#2C2C2C" />
                        <YAxis stroke="#2C2C2C" />
                        <Tooltip contentStyle={{ backgroundColor: '#FDFAF4', border: '1px solid #F2E4C4', borderRadius: '8px' }} />
                        <Legend />
                        <Bar dataKey="protein" fill="#3D6B3A" />
                        <Bar dataKey="carbs" fill="#E07B54" />
                        <Bar dataKey="fat" fill="#C8603A" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>

                  {macroData.length > 0 && (
                    <div className="card p-8">
                      <h2 className="font-display text-xl font-bold text-charcoal-900 mb-6">Today's Macro Distribution</h2>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie data={macroData} cx="50%" cy="50%" labelLine={false} label={({ name, value }) => `${name}: ${Math.round(value)}g`} outerRadius={80} dataKey="value">
                            {macroData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </div>
              </div>
            )}

            {nutritionData.length === 0 && !error && (
              <div className="text-center py-20">
                <BarChart3 className="w-12 h-12 text-charcoal-700/20 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-charcoal-800 mb-2">No nutrition data available</h3>
                <p className="text-charcoal-700/70">Your nutrition data will appear here once meals are logged.</p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
