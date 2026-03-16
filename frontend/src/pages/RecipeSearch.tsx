import { useState } from 'react'
import { Search, Filter, AlertCircle } from 'lucide-react'
import { api } from '@/lib/api'
import { Recipe } from '@/types/api'
import { RecipeCard } from '@/components/RecipeCard'
import { RecipeDetailModal } from '@/components/RecipeDetailModal'
import { SkeletonGrid } from '@/components/SkeletonLoader'

export function RecipeSearch() {
  const [query, setQuery] = useState('')
  const [topK, setTopK] = useState(10)
  const [rerank, setRerank] = useState(true)
  const [results, setResults] = useState<Recipe[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) { setError('Please enter a search query'); return }
    setLoading(true); setError(null); setSearched(true)
    try {
      const response = await api.searchRecipes({ query: query.trim(), top_k: topK, rerank })
      setResults(response.results || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to search recipes')
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-12">
          <h1 className="font-display text-4xl font-bold text-charcoal-900 mb-3">Recipe Search</h1>
          <p className="text-lg text-charcoal-700/70">Find recipes using semantic search with advanced filtering and reranking.</p>
        </div>

        <form onSubmit={handleSearch} className="card p-8 mb-12">
          <div className="space-y-6">
            <div>
              <label htmlFor="query" className="block text-sm font-mono font-medium text-charcoal-700/50 uppercase mb-2">Search Query</label>
              <div className="relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-charcoal-700/40" />
                <input id="query" type="text" value={query} onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g., 'healthy pasta with vegetables', 'quick breakfast ideas'..."
                  className="w-full pl-12 pr-4 py-3 bg-cream-50 border border-cream-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-forest-500 focus:border-transparent transition-all" />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label htmlFor="topK" className="block text-sm font-mono font-medium text-charcoal-700/50 uppercase mb-2">Results Count</label>
                <input id="topK" type="number" min="1" max="50" value={topK}
                  onChange={(e) => setTopK(Math.max(1, parseInt(e.target.value) || 10))}
                  className="w-full px-4 py-3 bg-cream-50 border border-cream-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-forest-500 focus:border-transparent transition-all" />
              </div>
              <div className="flex items-end">
                <label className="flex items-center gap-3 cursor-pointer">
                  <input type="checkbox" checked={rerank} onChange={(e) => setRerank(e.target.checked)}
                    className="w-5 h-5 rounded border-cream-300 text-forest-600 focus:ring-forest-500" />
                  <span className="text-sm font-medium text-charcoal-700">Enable Reranking</span>
                </label>
              </div>
              <div className="flex items-end">
                <button type="submit" disabled={loading} className="btn-primary w-full">
                  <Search className="w-5 h-5" />
                  {loading ? 'Searching...' : 'Search'}
                </button>
              </div>
            </div>
          </div>
        </form>

        {error && (
          <div className="mb-8 p-4 bg-terracotta-50 border border-terracotta-200 rounded-lg flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-terracotta-600 flex-shrink-0 mt-0.5" />
            <div><h3 className="font-medium text-terracotta-900">Search Error</h3><p className="text-sm text-terracotta-800 mt-1">{error}</p></div>
          </div>
        )}

        {loading ? <SkeletonGrid count={6} />
          : searched && results.length === 0 ? (
            <div className="text-center py-16">
              <Filter className="w-12 h-12 text-charcoal-700/20 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-charcoal-800 mb-2">No recipes found</h3>
              <p className="text-charcoal-700/70">Try adjusting your search query or filters.</p>
            </div>
          ) : (
            <>
              {searched && <div className="mb-6"><p className="text-sm text-charcoal-700/70">Found <span className="font-semibold text-charcoal-800">{results.length}</span> recipe{results.length !== 1 ? 's' : ''}</p></div>}
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
