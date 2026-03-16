import { useState } from 'react';
import { Clock, Star, ChefHat } from 'lucide-react';
import type { RecipeResult } from '../types/api';
import RecipeDetailModal from './RecipeDetailModal';

export default function RecipeCard({ recipe }: { recipe: RecipeResult }) {
  const [open, setOpen] = useState(false);
  const totalTime = (recipe.prep_time ?? 0) + (recipe.cook_time ?? 0);

  return (
    <>
      <div
        onClick={() => setOpen(true)}
        className="bg-white rounded-2xl p-5 shadow-sm border border-stone-100 hover:shadow-md hover:border-forest-200 transition-all cursor-pointer group"
      >
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-stone-800 group-hover:text-forest-700 transition-colors line-clamp-2">
            {recipe.name}
          </h3>
          {recipe.rating && (
            <div className="flex items-center gap-1 text-amber-500 text-sm ml-2 shrink-0">
              <Star size={13} fill="currentColor" />
              {recipe.rating.toFixed(1)}
            </div>
          )}
        </div>

        {recipe.description && (
          <p className="text-sm text-stone-500 line-clamp-2 mb-3">{recipe.description}</p>
        )}

        <div className="flex items-center gap-3 text-xs text-stone-400 mb-3">
          {totalTime > 0 && (
            <span className="flex items-center gap-1">
              <Clock size={12} /> {totalTime} min
            </span>
          )}
          {recipe.servings && (
            <span className="flex items-center gap-1">
              <ChefHat size={12} /> {recipe.servings} servings
            </span>
          )}
          {recipe.score !== undefined && (
            <span className="ml-auto text-forest-600 font-medium">
              {(recipe.score * 100).toFixed(0)}% match
            </span>
          )}
        </div>

        {recipe.nutrition && (
          <div className="grid grid-cols-4 gap-1 text-center bg-stone-50 rounded-xl p-2">
            {[
              { label: 'Cal', value: recipe.nutrition.calories },
              { label: 'Protein', value: recipe.nutrition.protein ? `${recipe.nutrition.protein}g` : undefined },
              { label: 'Carbs', value: recipe.nutrition.carbs ? `${recipe.nutrition.carbs}g` : undefined },
              { label: 'Fat', value: recipe.nutrition.fat ? `${recipe.nutrition.fat}g` : undefined },
            ].map(({ label, value }) =>
              value !== undefined ? (
                <div key={label}>
                  <div className="text-xs font-semibold text-stone-700">{value}</div>
                  <div className="text-[10px] text-stone-400">{label}</div>
                </div>
              ) : null
            )}
          </div>
        )}

        {recipe.dietary_tags && recipe.dietary_tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {recipe.dietary_tags.slice(0, 3).map((tag) => (
              <span key={tag} className="text-[10px] bg-forest-50 text-forest-700 px-2 py-0.5 rounded-full">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {open && <RecipeDetailModal recipe={recipe} onClose={() => setOpen(false)} />}
    </>
  );
}
