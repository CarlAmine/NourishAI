import { X, Clock, ChefHat, Star } from 'lucide-react';
import type { RecipeResult } from '../types/api';

export default function RecipeDetailModal({
  recipe,
  onClose,
}: {
  recipe: RecipeResult;
  onClose: () => void;
}) {
  const totalTime = (recipe.prep_time ?? 0) + (recipe.cook_time ?? 0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="sticky top-0 bg-white/95 backdrop-blur px-6 pt-6 pb-4 flex items-start justify-between border-b border-stone-100">
          <div>
            <h2 className="text-xl font-bold text-stone-800">{recipe.name}</h2>
            <div className="flex items-center gap-3 mt-1 text-sm text-stone-500">
              {totalTime > 0 && (
                <span className="flex items-center gap-1"><Clock size={13} />{totalTime} min</span>
              )}
              {recipe.servings && (
                <span className="flex items-center gap-1"><ChefHat size={13} />{recipe.servings} servings</span>
              )}
              {recipe.rating && (
                <span className="flex items-center gap-1 text-amber-500">
                  <Star size={13} fill="currentColor" />{recipe.rating.toFixed(1)}
                </span>
              )}
            </div>
          </div>
          <button onClick={onClose} className="text-stone-400 hover:text-stone-700 transition-colors">
            <X size={22} />
          </button>
        </div>

        <div className="p-6 space-y-6">
          {recipe.description && (
            <p className="text-stone-600">{recipe.description}</p>
          )}

          {recipe.nutrition && (
            <div className="grid grid-cols-4 gap-3 bg-forest-50 rounded-2xl p-4">
              {[
                { label: 'Calories', value: recipe.nutrition.calories },
                { label: 'Protein', value: recipe.nutrition.protein ? `${recipe.nutrition.protein}g` : undefined },
                { label: 'Carbs', value: recipe.nutrition.carbs ? `${recipe.nutrition.carbs}g` : undefined },
                { label: 'Fat', value: recipe.nutrition.fat ? `${recipe.nutrition.fat}g` : undefined },
              ].map(({ label, value }) =>
                value !== undefined ? (
                  <div key={label} className="text-center">
                    <div className="text-lg font-bold text-forest-700">{value}</div>
                    <div className="text-xs text-stone-500">{label}</div>
                  </div>
                ) : null
              )}
            </div>
          )}

          {recipe.ingredients && recipe.ingredients.length > 0 && (
            <div>
              <h3 className="font-semibold text-stone-700 mb-2">Ingredients</h3>
              <ul className="space-y-1">
                {recipe.ingredients.map((ing, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-stone-600">
                    <span className="text-forest-500 mt-0.5">•</span>{ing}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {recipe.instructions && recipe.instructions.length > 0 && (
            <div>
              <h3 className="font-semibold text-stone-700 mb-2">Instructions</h3>
              <ol className="space-y-2">
                {recipe.instructions.map((step, i) => (
                  <li key={i} className="flex gap-3 text-sm text-stone-600">
                    <span className="shrink-0 w-6 h-6 bg-forest-100 text-forest-700 rounded-full flex items-center justify-center text-xs font-bold">
                      {i + 1}
                    </span>
                    {step}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {recipe.dietary_tags && recipe.dietary_tags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {recipe.dietary_tags.map((tag) => (
                <span key={tag} className="text-xs bg-forest-50 text-forest-700 px-3 py-1 rounded-full border border-forest-100">
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
