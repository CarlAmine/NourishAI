import axios from 'axios';
import type {
  RecipeSearchRequest,
  RecommendRequest,
  RecipeSearchResponse,
  MealPlanResponse,
  NutritionResponse,
  HealthResponse,
} from '../types/api';

const BASE_URL = (import.meta.env.VITE_API_URL as string) ?? 'http://localhost:8000/api/v1';

const client = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const api = {
  health: (): Promise<HealthResponse> =>
    client.get('/health').then((r) => r.data),

  searchRecipes: (payload: RecipeSearchRequest): Promise<RecipeSearchResponse> =>
    client.post('/recipes/search', payload).then((r) => r.data),

  recommendRecipes: (payload: RecommendRequest): Promise<RecipeSearchResponse> =>
    client.post('/recipes/recommend', payload).then((r) => r.data),

  groundedRecommend: (payload: RecommendRequest): Promise<RecipeSearchResponse> =>
    client.post('/recipes/grounded_recommend', payload).then((r) => r.data),

  getMealPlan: (): Promise<MealPlanResponse> =>
    client.get('/meal_plans').then((r) => r.data),

  getNutrition: (): Promise<NutritionResponse> =>
    client.get('/nutrition').then((r) => r.data),
};
