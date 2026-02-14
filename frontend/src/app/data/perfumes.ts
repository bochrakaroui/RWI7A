export interface Perfume {
  id: string;
  name: string;
  brand: string;
  image: string;
  notes: {
    top: string[];
    middle: string[];
    base: string[];
  };
  rating: number;
  price: number;
  description: string;
}

export const perfumes: Perfume[] = [
  {
    id: "1",
    name: "Rose Elegance",
    brand: "Maison Luxe",
    image: "https://images.unsplash.com/photo-1618137585731-4c33c287d2dd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb3NlJTIwcGVyZnVtZSUyMGJvdHRsZXxlbnwxfHx8fDE3NzEwMjg0MzB8MA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Bergamot", "Pink Pepper"],
      middle: ["Rose", "Jasmine"],
      base: ["Musk", "Sandalwood"]
    },
    rating: 4.8,
    price: 145,
    description: "A timeless floral fragrance with elegant rose notes"
  },
  {
    id: "2",
    name: "Lavender Dreams",
    brand: "Aura Botanica",
    image: "https://images.unsplash.com/photo-1671492245104-bc7bb48ee567?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsYXZlbmRlciUyMHBlcmZ1bWUlMjBib3R0bGV8ZW58MXx8fHwxNzcxMDg3OTg5fDA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Lavender", "Lemon"],
      middle: ["Violet", "Lily"],
      base: ["Cedar", "Vanilla"]
    },
    rating: 4.6,
    price: 120,
    description: "Calming lavender with a touch of sweetness"
  },
  {
    id: "3",
    name: "Vanilla Noir",
    brand: "Essence Divine",
    image: "https://images.unsplash.com/photo-1602182479896-be4936b34c0a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx2YW5pbGxhJTIwcGVyZnVtZSUyMGJvdHRsZXxlbnwxfHx8fDE3NzEwODc5OTB8MA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Mandarin", "Saffron"],
      middle: ["Orange Blossom", "Tuberose"],
      base: ["Vanilla", "Tonka Bean", "Amber"]
    },
    rating: 4.9,
    price: 165,
    description: "Rich and warm vanilla with exotic spices"
  },
  {
    id: "4",
    name: "Citrus Bloom",
    brand: "Fresh & Pure",
    image: "https://images.unsplash.com/photo-1769625310883-6c87ed402d6f?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjaXRydXMlMjBwZXJmdW1lJTIwYm90dGxlfGVufDF8fHx8MTc3MTA4Nzk5MHww&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Lemon", "Grapefruit", "Bergamot"],
      middle: ["Neroli", "Magnolia"],
      base: ["White Musk", "Amber"]
    },
    rating: 4.5,
    price: 95,
    description: "Fresh and invigorating citrus blend"
  },
  {
    id: "5",
    name: "Jasmine Royale",
    brand: "Petale Précieux",
    image: "https://images.unsplash.com/photo-1750010387528-1fdf18f52a28?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxqYXNtaW5lJTIwcGVyZnVtZSUyMGVsZWdhbnR8ZW58MXx8fHwxNzcxMDg3OTkwfDA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Green Tea", "Pear"],
      middle: ["Jasmine", "Peony"],
      base: ["Patchouli", "White Musk"]
    },
    rating: 4.7,
    price: 130,
    description: "Sophisticated jasmine with a modern twist"
  },
  {
    id: "6",
    name: "Amber Mystique",
    brand: "Orient Luxe",
    image: "https://images.unsplash.com/photo-1759793499912-625d49ae6087?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhbWJlciUyMHBlcmZ1bWUlMjBib3R0bGV8ZW58MXx8fHwxNzcxMDg3OTkwfDA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Cardamom", "Cinnamon"],
      middle: ["Iris", "Ylang-Ylang"],
      base: ["Amber", "Oud", "Benzoin"]
    },
    rating: 4.8,
    price: 180,
    description: "Mysterious and sensual oriental fragrance"
  },
  {
    id: "7",
    name: "Pink Blossom",
    brand: "Florale Chic",
    image: "https://images.unsplash.com/photo-1736611966591-406d96f8985a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwaW5rJTIwcGVyZnVtZSUyMGJvdHRsZSUyMGZlbWluaW5lfGVufDF8fHx8MTc3MTAxMTU5N3ww&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Strawberry", "Raspberry"],
      middle: ["Peony", "Freesia"],
      base: ["Cashmere", "Vanilla"]
    },
    rating: 4.6,
    price: 110,
    description: "Playful and feminine with fruity-floral notes"
  },
  {
    id: "8",
    name: "Serene Garden",
    brand: "Nature's Whisper",
    image: "https://images.unsplash.com/photo-1770301410072-f6ef6dad65b2?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxsdXh1cnklMjBwZXJmdW1lJTIwYm90dGxlJTIwZWxlZ2FudHxlbnwxfHx8fDE3NzEwMTk5OTl8MA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Green Apple", "Basil"],
      middle: ["Gardenia", "Lotus"],
      base: ["Vetiver", "Moss"]
    },
    rating: 4.4,
    price: 105,
    description: "Fresh garden flowers with green notes"
  },
  {
    id: "9",
    name: "Velvet Petals",
    brand: "Maison Luxe",
    image: "https://images.unsplash.com/photo-1618137585731-4c33c287d2dd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxyb3NlJTIwcGVyZnVtZSUyMGJvdHRsZXxlbnwxfHx8fDE3NzEwMjg0MzB8MA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Red Berries", "Orange"],
      middle: ["Rose", "Violet"],
      base: ["Suede", "Praline"]
    },
    rating: 4.7,
    price: 155,
    description: "Velvety rose with gourmand undertones"
  },
  {
    id: "10",
    name: "Moonlight Musk",
    brand: "Essence Divine",
    image: "https://images.unsplash.com/photo-1602182479896-be4936b34c0a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx2YW5pbGxhJTIwcGVyZnVtZSUyMGJvdHRsZXxlbnwxfHx8fDE3NzEwODc5OTB8MA&ixlib=rb-4.1.0&q=80&w=1080",
    notes: {
      top: ["Aldehydes", "Neroli"],
      middle: ["Iris", "Mimosa"],
      base: ["White Musk", "Cashmere", "Vanilla"]
    },
    rating: 4.9,
    price: 170,
    description: "Clean and powdery musk with a luminous finish"
  }
];
