const API_BASE = 'http://localhost:8000';

export interface PerfumeInfo {
  name: string;
  brand: string;
  rating: number;
  review_count: number;
  similarity?: number;
  brand_tier?: string;
}

export async function searchPerfumes(query: string, brand?: string, topN = 10) {
  const res = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, brand, top_n: topN })
  });
  return res.json();
}

export async function getRecommendations(perfumeName: string, brand?: string, topN = 5) {
  const res = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ perfume_name: perfumeName, brand, top_n: topN })
  });
  return res.json();
}

export async function getBrands() {
  const res = await fetch(`${API_BASE}/brands`);
  return res.json();
}