import { useEffect, useState } from 'react'
import { Calendar, Download, AlertCircle, Loader } from 'lucide-react'
import { api } from '@/lib/api'
import { MealPlan, Recipe } from '@/types/api'
import { RecipeDetailModal } from '@/components/RecipeDetailModal'

export function MealPlanPage() {
  const [mealPlans, setMealPlans] = useState<MealPlan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)

  useEffect(() => { loadMealPlans() }, [])

  const loadMealPlans = async () => {
    setLoading(true); setError(null)
    try {
      const response = await api.getMealPlans()
      setMealPlans(response.meal_plans || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load meal plans')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-start justify-between mb-12">
          <div>
            <h1 className="font-display text-4xl font-bold text-charcoal-900 mb-3">Weekly Meal Plan</h1>
            <p className="text-lg text-charcoal-700/70">Your AI-generated meal plan for the week with breakfast, lunch, and dinner.</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => window.print()} className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-cream-200 text-charcoal-800 font-medium rounded-lg hover:bg-cream-300 transition-colors">
              <Download className="w-4 h-4" /> Print
            </button>
          </div>
        </div>

        {error && (
          <div className="mb-8 p-4 bg-terracotta-50 border border-terracotta-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-terracotta-600 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-medium text-terracotta-900">Error</h3>
              <p className="text-sm text-terracotta-800 mt-1">{error}</p>
              <button onClick={loadMealPlans} className="mt-2 text-sm font-medium text-terracotta-700 hover:text-terracotta-900 underline">Try Again</button>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader className="w-8 h-8 text-forest-500 mx-auto mb-4 animate-spin" />
              <p className="text-charcoal-700">Loading your meal plan...</p>
            </div>
          </div>
        )}

        {!loading && mealPlans.length > 0 && (
          <div className="space-y-8">
            {mealPlans.map((plan, planIdx) => (
              <div key={planIdx} className="card p-8">
                <h2 className="font-display text-2xl font-bold text-charcoal-900 mb-6">
                  {new Date(plan.date).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {(['breakfast', 'lunch', 'dinner'] as const).map((mealType) => (
                    <div key={mealType} className={`rounded-xl p-6 border ${
                      mealType === 'lunch' ? 'bg-gradient-to-br from-forest-50 to-cream-50 border-forest-200/50' : 'bg-gradient-to-br from-terracotta-50 to-cream-50 border-terracotta-200/50'
                    }`}>
                      <h3 className={`text-sm font-mono font-bold uppercase mb-4 ${ mealType === 'lunch' ? 'text-forest-700' : 'text-terracotta-700' }`}>
                        {mealType}
                      </h3>
                      {plan.meals[mealType] ? (
                        <MealCard recipe={plan.meals[mealType]!} onViewDetails={setSelectedRecipe} />
                      ) : (
                        <div className="text-center py-8 text-charcoal-700/50">
                          <Calendar className="w-8 h-8 mx-auto mb-2 opacity-30" />
                          <p className="text-sm">No meal scheduled</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && mealPlans.length === 0 && !error && (
          <div className="text-center py-20">
            <Calendar className="w-12 h-12 text-charcoal-700/20 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-charcoal-800 mb-2">No meal plans available</h3>
            <p className="text-charcoal-700/70">Your meal plans will appear here once they are generated.</p>
          </div>
        )}
      </div>
      <RecipeDetailModal recipe={selectedRecipe} onClose={() => setSelectedRecipe(null)} />
    </div>
  )
}

function MealCard({ recipe, onViewDetails }: { recipe: Recipe; onViewDetails: (r: Recipe) => void }) {
  const nutrition = recipe.nutrition || {}
  return (
    <button onClick={() => onViewDetails(recipe)} className="w-full text-left hover:opacity-75 transition-opacity">
      <h4 className="font-display font-bold text-charcoal-900 mb-3 line-clamp-2">{recipe.name}</h4>
      {recipe.minutes && <div className="text-xs text-charcoal-700/70 mb-3">⏱️ {recipe.minutes} min</div>}
      <div className="space-y-2 text-xs">
        {nutrition.calories && <div className="flex justify-between"><span className="text-charcoal-700/70">Calories:</span><span className="font-mono font-bold text-charcoal-900">{Math.round(nutrition.calories)} kcal</span></div>}
        {nutrition.protein && <div className="flex justify-between"><span className="text-charcoal-700/70">Protein:</span><span className="font-mono font-bold text-charcoal-900">{Math.round(nutrition.protein)}g</span></div>}
        {nutrition.carbs && <div className="flex justify-between"><span className="text-charcoal-700/70">Carbs:</span><span className="font-mono font-bold text-charcoal-900">{Math.round(nutrition.carbs)}g</span></div>}
      </div>
      <div className="mt-4 w-full text-xs font-medium text-forest-600 hover:text-forest-700 py-2 px-3 bg-forest-50 rounded hover:bg-forest-100 transition-colors text-center">View Details</div>
    </button>
  )
}
