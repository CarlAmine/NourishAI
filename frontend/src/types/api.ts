export interface NutritionInfo {
  calories: number | null; total_fat: number | null; total_sugar: number | null;
  sodium: number | null; protein: number | null; saturated_fat: number | null;
}
export interface RecipeDetail {
  name: string; minutes: number | null; ingredients: string[]; steps: string[]; nutrition: NutritionInfo;
}
export interface ImagePredictResponse {
  predicted_class: string; recipe: RecipeDetail | null; error: string | null;
}
export interface RecipeSuggestion { match_score: number; recipe_text: string; }
export interface SuggestResponse { results: RecipeSuggestion[]; }
export type AppMode = 'image' | 'ingredients'
export interface ApiError { detail: string; }
