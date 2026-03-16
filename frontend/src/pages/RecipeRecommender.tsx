import { useState } from 'react'
import { Zap, X, AlertCircle, Plus } from 'lucide-react'
import { api } from '@/lib/api'
import { Recipe } from '@/types/api'
import { RecipeCard } from '@/components/RecipeCard'
import { RecipeDetailModal } from '@/components/RecipeDetailModal'
import { SkeletonGrid } from '@/components/SkeletonLoader'

export function RecipeRecommender() {
  const [ingredients, setIngredients] = useState<string[]>([])
  const [ingredientInput, setIngredientInput] = useState('')
  const [dietaryNotes, setDietaryNotes] = useState('')
  const [topK, setTopK] = useState(10)
  const [results, setResults] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [searched, setSearched] = useState(false)

  const handleAddIngredient = () => {
    const trimmed = ingredientInput.trim()
    if (trimmed && !ingredients.includes(trimmed)) {
      setIngredients([...ingredients, trimmed])
      setIngredientInput('')
    }
  }

  const handleRecommend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (ingredients.length === 0) { setError('Please add at least one ingredient'); return }
    setLoading(true); setError(null); setSearched(true)
    try {
      const response = await api.recommendRecipes({ ingredients, dietary_notes: dietaryNotes || undefined, top_k: topK })
      setResults(response.results || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get recommendations')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-12">
          <h1 className="font-display text-4xl font-bold text-charcoal-900 mb-3">Recipe Recommender</h1>
          <p className="text-lg text-charcoal-700/70">Get personalized recipe suggestions based on your available ingredients and dietary preferences.</p>
        </div>

        <form onSubmit={handleRecommend} className="card p-8 mb-12">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-mono font-medium text-charcoal-700/50 uppercase mb-2">Ingredients</label>
              <div className="flex gap-2 mb-3">
                <input type="text" value={ingredientInput} onChange={(e) => setIngredientInput(e.target.value)}
                  onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAddIngredient() } }}
                  placeholder="e.g., 'chicken', 'tomato', 'garlic'..."
                  className="flex-1 px-4 py-3 bg-cream-50 border border-cream-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-forest-500 focus:border-transparent transition-all" />
                <button type="button" onClick={handleAddIngredient} className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-forest-500 text-white font-medium rounded-lg hover:bg-forest-600 transition-colors">
                  <Plus className="w-4 h-4" /> Add
                </button>
              </div>
              {ingredients.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {ingredients.map((ingredient, idx) => (
                    <div key={idx} className="inline-flex items-center gap-2 px-3 py-1 bg-forest-100 text-forest-700 rounded-full text-sm font-medium">
                      {ingredient}
                      <button type="button" onClick={() => setIngredients(ingredients.filter((_, i) => i !== idx))} className="hover:text-forest-900 transition-colors">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-mono font-medium text-charcoal-700/50 uppercase mb-2">Dietary Preferences (Optional)</label>
              <textarea value={dietaryNotes} onChange={(e) => setDietaryNotes(e.target.value)}
                placeholder="e.g., 'gluten-free, high-protein, low-carb'..." rows={3}
                className="w-full px-4 py-3 bg-cream-50 border border-cream-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-forest-500 focus:border-transparent transition-all resize-none" />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-mono font-medium text-charcoal-700/50 uppercase mb-2">Results Count</label>
                <input type="number" min="1" max="50" value={topK} onChange={(e) => setTopK(Math.max(1, parseInt(e.target.value) || 10))}
                  className="w-full px-4 py-3 bg-cream-50 border border-cream-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-forest-500 focus:border-transparent transition-all" />
              </div>
              <div className="flex items-end">
                <button type="submit" disabled={loading || ingredients.length === 0} className="btn-primary w-full">
                  <Zap className="w-5 h-5" />
                  {loading ? 'Getting Recommendations...' : 'Get Recommendations'}
                </button>
              </div>
            </div>
          </div>
        </form>

        {error && (
          <div className="mb-8 p-4 bg-terracotta-50 border border-terracotta-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-terracotta-600 flex-shrink-0 mt-0.5" />
            <div><h3 className="font-medium text-terracotta-900">Error</h3><p className="text-sm text-terracotta-800 mt-1">{error}</p></div>
          </div>
        )}

        {loading ? <SkeletonGrid count={6} />
          : searched && results.length === 0 ? (
            <div className="text-center py-16">
              <Zap className="w-12 h-12 text-charcoal-700/20 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-charcoal-800 mb-2">No recommendations found</h3>
              <p className="text-charcoal-700/70">Try adding different ingredients or adjusting your preferences.</p>
            </div>
          ) : (
            <>
              {searched && <div className="mb-6"><p className="text-sm text-charcoal-700/70">Found <span className="font-semibold text-charcoal-800">{results.length}</span> recommendation{results.length !== 1 ? 's' : ''}</p></div>}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {results.map((recipe, idx) => <RecipeCard key={`${recipe.name}-${idx}`} recipe={recipe} onViewDetails={setSelectedRecipe} />)}
              </div>
            </>
          )}
      </div>
      <RecipeDetailModal recipe={selectedRecipe} onClose={() => setSelectedRecipe(null)} />
    </div>
  )
}
