<template>
  <div class="p-6 space-y-6">
    <!-- Keywords Section -->
    <div v-if="currentSDG" class="flex gap-2 flex-wrap">
      <span
        v-for="keyword in currentSDG.keywords"
        :key="keyword"
        class="px-2 py-1 text-sm text-white bg-blue-500 rounded-full"
      >
        {{ keyword }}
      </span>
    </div>

    <!-- SDG Card -->
    <div
      v-if="currentSDG"
      class="flex flex-col items-center p-4 border rounded-lg shadow-lg bg-white"
    >
      <!-- SDG Icon -->
      <img
        :src="`data:image/svg+xml;base64,${selectedSDG.icon}`"
        :alt="`SDG ${selectedSDG.id} Icon`"
        class="w-16 h-16 mb-4"
      />


      <!-- SDG Title -->
      <h2 class="text-lg font-bold text-gray-900">
        {{ currentSDG.title }}
      </h2>

      <!-- SDG Short Title -->
      <p class="text-sm text-gray-600 mt-1">
        {{ currentSDG.shortTitle }}
      </p>

      <!-- Catchy Explanation -->
      <p class="text-center text-gray-700 mt-4">
        {{ currentSDG.catchyExplanation }}
      </p>

      <LevelSelector></LevelSelector>
    </div>
    <div v-else>
      No SDG Selected
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useSDGsStore } from "~/stores/sdgs";
import LevelSelector from "~/components/LevelSelector.vue";

const sdgsStore = useSDGsStore();

// Get the selected SDG from the store
const selectedSDG = computed(() => {
  const sdgId = sdgsStore.getSelectedSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Computed property to get the selected SDG by mapping the index from the store to the sdgs array
const currentSDG = computed(() => {
  const selectedSDGIndex = sdgsStore.getSelectedSDG; // Index of the selected SDG
  return sdgs.find((sdg) => sdg.id === selectedSDGIndex) || null; // Match the SDG by ID
});

const sdgs = [
  {
    id: 1,
    title: "No Poverty",
    shortTitle: "End Poverty",
    keywords: ["poverty", "equality", "sustainability"],
    catchyExplanation:
      "Imagine a world where everyone has access to basic needs like food, shelter, and education. SDG 1 is the first step toward eliminating poverty globally and ensuring everyone gets a fair chance."
  },
  {
    id: 2,
    title: "Zero Hunger",
    shortTitle: "End Hunger",
    keywords: ["hunger", "food security", "nutrition"],
    catchyExplanation:
      "Ending hunger is more than feeding people—it’s about sustainable farming and fair distribution of food. SDG 2 is your gateway to a world without hunger."
  },
  {
    id: 3,
    title: "Good Health and Well-Being",
    shortTitle: "Health for All",
    keywords: ["health", "well-being", "medicine"],
    catchyExplanation:
      "Health is wealth! SDG 3 focuses on ensuring healthy lives and promoting well-being for everyone, everywhere. From vaccines to mental health, this goal touches us all."
  },
  {
    id: 4,
    title: "Quality Education",
    shortTitle: "Education for All",
    keywords: ["education", "learning", "equality"],
    catchyExplanation:
      "Education is the key to unlocking the potential of individuals and communities. SDG 4 aims to provide inclusive, equitable, and quality education for everyone."
  },
  {
    id: 5,
    title: "Gender Equality",
    shortTitle: "Equality Now",
    keywords: ["gender equality", "women empowerment", "rights"],
    catchyExplanation:
      "A fair and just world is one where everyone is equal. SDG 5 emphasizes empowering women and girls, ensuring they have equal opportunities in every sphere of life."
  },
  {
    id: 6,
    title: "Clean Water and Sanitation",
    shortTitle: "Water for All",
    keywords: ["water", "sanitation", "hygiene"],
    catchyExplanation:
      "Clean water and sanitation are essential for health and well-being. SDG 6 works towards universal access to safe water and sanitation facilities."
  },
  {
    id: 7,
    title: "Affordable and Clean Energy",
    shortTitle: "Clean Energy",
    keywords: ["energy", "renewables", "sustainability"],
    catchyExplanation:
      "Power the world sustainably! SDG 7 is about ensuring access to affordable, reliable, and modern energy for everyone, while protecting the planet."
  },
  {
    id: 8,
    title: "Decent Work and Economic Growth",
    shortTitle: "Work & Growth",
    keywords: ["jobs", "economic growth", "sustainability"],
    catchyExplanation:
      "Decent work is the backbone of economic growth. SDG 8 ensures productive employment and fair conditions for all, while promoting sustainable development."
  },
  {
    id: 9,
    title: "Industry, Innovation, and Infrastructure",
    shortTitle: "Innovation Matters",
    keywords: ["innovation", "industry", "infrastructure"],
    catchyExplanation:
      "Infrastructure and innovation drive progress. SDG 9 focuses on building resilient infrastructure and fostering innovation for sustainable industrial growth."
  },
  {
    id: 10,
    title: "Reduced Inequalities",
    shortTitle: "Equal Opportunities",
    keywords: ["inequality", "inclusion", "justice"],
    catchyExplanation:
      "Inequality holds us back. SDG 10 seeks to reduce disparities within and among countries, ensuring fair opportunities for everyone."
  },
  {
    id: 11,
    title: "Sustainable Cities and Communities",
    shortTitle: "Cities for All",
    keywords: ["cities", "sustainability", "communities"],
    catchyExplanation:
      "Imagine a city where everyone thrives. SDG 11 focuses on making cities inclusive, safe, resilient, and sustainable for all inhabitants."
  },
  {
    id: 12,
    title: "Responsible Consumption and Production",
    shortTitle: "Consume Wisely",
    keywords: ["sustainability", "production", "consumption"],
    catchyExplanation:
      "Our choices shape the future. SDG 12 promotes sustainable consumption and production patterns to protect our planet’s resources."
  },
  {
    id: 13,
    title: "Climate Action",
    shortTitle: "Act on Climate",
    keywords: ["climate", "action", "sustainability"],
    catchyExplanation:
      "The time to act is now! SDG 13 calls for urgent action to combat climate change and its impacts, securing a sustainable future for all."
  },
  {
    id: 14,
    title: "Life Below Water",
    shortTitle: "Protect Oceans",
    keywords: ["oceans", "marine life", "biodiversity"],
    catchyExplanation:
      "Oceans are vital for life on Earth. SDG 14 works to conserve and sustainably use marine resources for future generations."
  },
  {
    id: 15,
    title: "Life on Land",
    shortTitle: "Protect Nature",
    keywords: ["forests", "biodiversity", "ecosystems"],
    catchyExplanation:
      "Our ecosystems sustain us. SDG 15 promotes sustainable use of terrestrial ecosystems and halting biodiversity loss."
  },
  {
    id: 16,
    title: "Peace, Justice, and Strong Institutions",
    shortTitle: "Justice for All",
    keywords: ["peace", "justice", "institutions"],
    catchyExplanation:
      "A peaceful society is a thriving society. SDG 16 aims to promote just, inclusive, and peaceful communities around the globe."
  },
  {
    id: 17,
    title: "Partnerships for the Goals",
    shortTitle: "Global Partnerships",
    keywords: ["partnerships", "collaboration", "global goals"],
    catchyExplanation:
      "Achieving the SDGs requires teamwork. SDG 17 fosters partnerships to strengthen implementation of all the global goals."
  }
];
</script>


