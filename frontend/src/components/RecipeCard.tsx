import { Recipe } from '@/types/api'
import { Clock, Flame, Droplet } from 'lucide-react'
import { useState } from 'react'

interface RecipeCardProps {
  recipe: Recipe
  onViewDetails?: (recipe: Recipe) => void
}

export function RecipeCard({ recipe, onViewDetails }: RecipeCardProps) {
  const [isHovered, setIsHovered] = useState(false)

  const nutrition = recipe.nutrition || {}
  const matchScore = recipe.match_score ? Math.round(recipe.match_score * 100) : null

  return (
    <div
      className="card p-6 hover:shadow-md transition-all duration-300 cursor-pointer group"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onViewDetails?.(recipe)}
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-display text-lg font-bold text-charcoal-800 group-hover:text-forest-600 transition-colors line-clamp-2">
            {recipe.name}
          </h3>
          {recipe.minutes && (
            <div className="flex items-center gap-1 text-sm text-charcoal-700/60 mt-1">
              <Clock className="w-3.5 h-3.5" />
              <span>{recipe.minutes} min</span>
            </div>
          )}
        </div>
        {matchScore && (
          <div className="ml-4 flex-shrink-0">
            <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-forest-50 border-2 border-forest-200">
              <span className="font-mono font-bold text-forest-700 text-sm">{matchScore}%</span>
            </div>
          </div>
        )}
      </div>

      {recipe.tags && recipe.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {recipe.tags.slice(0, 3).map((tag, idx) => (
            <span key={idx} className="tag-green">{tag}</span>
          ))}
          {recipe.tags.length > 3 && <span className="text-xs text-charcoal-600/60">+{recipe.tags.length - 3}</span>}
        </div>
      )}

      <div className="grid grid-cols-3 gap-3 pt-4 border-t border-cream-200">
        {nutrition.calories && (
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Flame className="w-3.5 h-3.5 text-terracotta-500" />
            </div>
            <div className="text-sm font-mono font-bold text-charcoal-800">{Math.round(nutrition.calories)}</div>
            <div className="text-xs text-charcoal-600/60">kcal</div>
          </div>
        )}
        {nutrition.protein && (
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Droplet className="w-3.5 h-3.5 text-forest-500" />
            </div>
            <div className="text-sm font-mono font-bold text-charcoal-800">{Math.round(nutrition.protein)}g</div>
            <div className="text-xs text-charcoal-600/60">protein</div>
          </div>
        )}
        {nutrition.carbs && (
          <div className="text-center">
            <div className="flex items-center justify-center gap-1 mb-1">
              <Droplet className="w-3.5 h-3.5 text-terracotta-400" />
            </div>
            <div className="text-sm font-mono font-bold text-charcoal-800">{Math.round(nutrition.carbs)}g</div>
            <div className="text-xs text-charcoal-600/60">carbs</div>
          </div>
        )}
      </div>

      {recipe.ingredients && recipe.ingredients.length > 0 && (
        <div className="mt-4 pt-4 border-t border-cream-200">
          <p className="text-xs font-mono font-medium text-charcoal-700/50 uppercase mb-2">Ingredients</p>
          <ul className="space-y-1">
            {recipe.ingredients.slice(0, 3).map((ingredient, idx) => (
              <li key={idx} className="text-sm text-charcoal-700 line-clamp-1">• {ingredient}</li>
            ))}
            {recipe.ingredients.length > 3 && (
              <li className="text-xs text-charcoal-600/60">+{recipe.ingredients.length - 3} more</li>
            )}
          </ul>
        </div>
      )}

      {isHovered && (
        <button className="btn-primary w-full mt-4">View Recipe</button>
      )}
    </div>
  )
}
