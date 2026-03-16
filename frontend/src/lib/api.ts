import axios, { AxiosError } from 'axios'
import type {
  ImagePredictResponse,
  SuggestResponse,
  ApiError,
  SearchRequest,
  SearchResponse,
  RecommendRequest,
  RecommendResponse,
  MealPlanResponse,
  NutritionResponse,
} from '@/types/api'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
const client = axios.create({ baseURL: BASE_URL, timeout: 60_000 })

function extractError(err: unknown): string {
  if (err instanceof AxiosError) {
    const data = err.response?.data as ApiError | undefined
    return data?.detail ?? err.message
  }
  if (err instanceof Error) return err.message
  return 'An unexpected error occurred.'
}

export const api = {
  async predictFromImage(file: File): Promise<ImagePredictResponse> {
    const form = new FormData()
    form.append('file', file)
    try {
      const { data } = await client.post<ImagePredictResponse>('/recipes/predict-image', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async suggestByIngredients(ingredients: string, topK = 3): Promise<SuggestResponse> {
    try {
      const { data } = await client.post<SuggestResponse>('/recipes/suggest', { ingredients, top_k: topK })
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async lookupRecipe(name: string): Promise<ImagePredictResponse> {
    try {
      const { data } = await client.get<ImagePredictResponse>(`/recipes/lookup/${encodeURIComponent(name)}`)
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async searchRecipes(request: SearchRequest): Promise<SearchResponse> {
    try {
      const { data } = await client.post<SearchResponse>('/recipes/search', request)
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async recommendRecipes(request: RecommendRequest): Promise<RecommendResponse> {
    try {
      const { data } = await client.post<RecommendResponse>('/recipes/recommend', request)
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async getGroundedRecommendations(request: RecommendRequest): Promise<RecommendResponse> {
    try {
      const { data } = await client.post<RecommendResponse>('/recipes/grounded_recommend', request)
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async getMealPlans(): Promise<MealPlanResponse> {
    try {
      const { data } = await client.get<MealPlanResponse>('/meal_plans')
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async getNutritionData(): Promise<NutritionResponse> {
    try {
      const { data } = await client.get<NutritionResponse>('/nutrition')
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },

  async healthCheck(): Promise<{ status: string }> {
    try {
      const { data } = await client.get<{ status: string }>('/health')
      return data
    } catch (err) {
      throw new Error(extractError(err))
    }
  },
}
