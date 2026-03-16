import { Recipe } from '@/types/api'
import { X, Clock, Flame, Droplet } from 'lucide-react'
import { useEffect } from 'react'

interface RecipeDetailModalProps {
  recipe: Recipe | null
  onClose: () => void
}

export function RecipeDetailModal({ recipe, onClose }: RecipeDetailModalProps) {
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [onClose])

  if (!recipe) return null

  const nutrition = recipe.nutrition || {}

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="sticky top-0 bg-gradient-to-r from-forest-50 to-cream-50 border-b border-cream-200 p-6 flex items-start justify-between">
          <div className="flex-1">
            <h2 className="font-display text-2xl font-bold text-charcoal-800 mb-2">{recipe.name}</h2>
            {recipe.minutes && (
              <div className="flex items-center gap-2 text-charcoal-700">
                <Clock className="w-4 h-4" />
                <span className="text-sm">{recipe.minutes} minutes</span>
              </div>
            )}
          </div>
          <button onClick={onClose} className="p-2 hover:bg-cream-200 rounded-lg transition-colors">
            <X className="w-6 h-6 text-charcoal-700" />
          </button>
        </div>

        <div className="p-6 space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {nutrition.calories && (
              <div className="bg-terracotta-50 rounded-xl p-4 border border-terracotta-200">
                <div className="flex items-center gap-2 mb-2">
                  <Flame className="w-4 h-4 text-terracotta-500" />
                  <span className="text-xs font-mono font-medium text-terracotta-700 uppercase">Calories</span>
                </div>
                <div className="text-2xl font-bold text-terracotta-700">{Math.round(nutrition.calories)}</div>
                <div className="text-xs text-terracotta-600">kcal</div>
              </div>
            )}
            {nutrition.protein && (
              <div className="bg-forest-50 rounded-xl p-4 border border-forest-200">
                <div className="flex items-center gap-2 mb-2">
                  <Droplet className="w-4 h-4 text-forest-500" />
                  <span className="text-xs font-mono font-medium text-forest-700 uppercase">Protein</span>
                </div>
                <div className="text-2xl font-bold text-forest-700">{Math.round(nutrition.protein)}</div>
                <div className="text-xs text-forest-600">grams</div>
              </div>
            )}
            {nutrition.carbs && (
              <div className="bg-terracotta-50 rounded-xl p-4 border border-terracotta-200">
                <div className="flex items-center gap-2 mb-2">
                  <Droplet className="w-4 h-4 text-terracotta-400" />
                  <span className="text-xs font-mono font-medium text-terracotta-700 uppercase">Carbs</span>
                </div>
                <div className="text-2xl font-bold text-terracotta-700">{Math.round(nutrition.carbs)}</div>
                <div className="text-xs text-terracotta-600">grams</div>
              </div>
            )}
            {nutrition.total_fat && (
              <div className="bg-cream-100 rounded-xl p-4 border border-cream-300">
                <div className="flex items-center gap-2 mb-2">
                  <Droplet className="w-4 h-4 text-charcoal-600" />
                  <span className="text-xs font-mono font-medium text-charcoal-700 uppercase">Fat</span>
                </div>
                <div className="text-2xl font-bold text-charcoal-700">{Math.round(nutrition.total_fat)}</div>
                <div className="text-xs text-charcoal-600">grams</div>
              </div>
            )}
          </div>

          {recipe.ingredients && recipe.ingredients.length > 0 && (
            <div>
              <h3 className="text-sm font-mono font-bold uppercase text-charcoal-700/50 mb-3">Ingredients</h3>
              <ul className="space-y-2">
                {recipe.ingredients.map((ingredient, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-charcoal-700">
                    <span className="text-forest-500 font-bold mt-0.5">•</span>
                    <span>{ingredient}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recipe.steps && recipe.steps.length > 0 && (
            <div>
              <h3 className="text-sm font-mono font-bold uppercase text-charcoal-700/50 mb-3">Instructions</h3>
              <ol className="space-y-3">
                {recipe.steps.map((step, idx) => (
                  <li key={idx} className="flex gap-3 text-charcoal-700">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-forest-100 text-forest-700 flex items-center justify-center text-xs font-bold">
                      {idx + 1}
                    </span>
                    <span className="pt-0.5">{step}</span>
                  </li>
                ))}
              </ol>
            </div>
          )}
        </div>

        <div className="sticky bottom-0 bg-cream-50 border-t border-cream-200 p-6 flex gap-3">
          <button onClick={onClose} className="flex-1 px-6 py-3 bg-cream-200 text-charcoal-800 font-medium rounded-xl hover:bg-cream-300 transition-colors">
            Close
          </button>
          <button className="flex-1 btn-primary">Add to Meal Plan</button>
        </div>
      </div>
    </div>
  )
}
