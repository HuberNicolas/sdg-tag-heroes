// Icon of a topic (collection). Topics come from BERTopic, so their names are not known in advance: the thesis
// dataset has hand-picked icons for its 21 topic names, every other name gets an icon from SDG-related keywords in
// it, and a neutral tag when nothing matches.

// Hand-picked icons of the topics of the thesis dataset
const thesisTopicIcons: Record<string, string> = {
  "Cancer Imaging": "mdi:radiology-box",
  "Heart Imaging": "mdi:heart-box",
  "Swiss Research": "gg:swiss",
  "Cell Signaling": "mdi:bio",
  "Mental Health": "mdi:meditation",
  "Brain Function": "mdi:head-cog",
  "Ecosystem Changes": "material-symbols:nature",
  "Pandemic Studies": "fa-solid:virus",
  "Sustainability Policies": "carbon:sustainability",
  "Particle Physics": "ion:planet",
  "Molecular Chemistry": "material-symbols:science",
  "Dental Implants": "mdi:tooth",
  "Financial Models": "fa-solid:chart-line",
  "Bacterial Resistance": "mdi:bacteria",
  "Data Processing": "icon-park-outline:data",
  "Mathematical Models": "mdi:math-compass",
  "Neural Networks": "mdi:brain",
  "Environmental Sensing": "mdi:leaf",
  "Tech Governance": "mdi:shield-account",
  "Genetic Mutations": "mdi:dna",
  "Material Science": "mdi:flask",
};

// Keyword patterns, most specific first; the first match wins. Only mdi icons, which are bundled (nuxt.config.ts)
const keywordIcons: [RegExp, string][] = [
  [/antimicrobial|bacteri|antibiotic/, "mdi:bacteria"],
  [/vaccin|immunis|immuniz/, "mdi:needle"],
  [/pandemic|virus|viral|infectious/, "mdi:virus"],
  [/mental|mindful|wellbeing|well-being|depress/, "mdi:meditation"],
  [/smallholder|farm|agricultur|crop|food|hunger|harvest/, "mdi:barley"],
  [/health|hygiene|nutrition|disease|hospital|maternal|mortality|medic/, "mdi:heart-pulse"],
  [/water|drinking|sanitation|irrigation/, "mdi:water"],
  [/solar|renewable|energy|microgrid|electric|wind power/, "mdi:solar-power"],
  [/ocean|marine|coastal|coral|acidification|fisher/, "mdi:waves"],
  [/plastic|circular|recycl|waste/, "mdi:recycle"],
  [/climate|heat|emission|carbon|warming/, "mdi:thermometer-alert"],
  [/disaster|resilien|flood|drought/, "mdi:weather-pouring"],
  [/gender|women|girls/, "mdi:gender-male-female"],
  [/inequalit|disparit|inclusion|discriminat/, "mdi:scale-balance"],
  [/urban|city|cities|municipal|housing|transport/, "mdi:city"],
  [/poverty|microfinance|income|wealth|cash transfer/, "mdi:hand-coin"],
  [/violence|peace|conflict|crime/, "mdi:bird"],
  [/corporate|company|companies|firm|reporting|business/, "mdi:office-building"],
  [/justice|law|legal|governance|corruption|procurement|policymaker|policy/, "mdi:gavel"],
  [/education|school|learning|literacy|teacher/, "mdi:school"],
  [/econom|employment|labour|labor|market|finance|growth|trade/, "mdi:chart-line"],
  [/innovation|industr|infrastructure|technolog|digital/, "mdi:factory"],
  [/ecosystem|land use|forest|biodiversity|habitat|species|soil/, "mdi:tree"],
  [/partnership|cooperat|collaborat|community/, "mdi:handshake"],
];

const fallbackIcon = "mdi:tag-outline";

export function topicIcon(name?: string | null): string {
  if (!name) return fallbackIcon;
  if (thesisTopicIcons[name]) return thesisTopicIcons[name];
  const lower = name.toLowerCase();
  return keywordIcons.find(([pattern]) => pattern.test(lower))?.[1] ?? fallbackIcon;
}
