# Gamified Labeling


## Fundamentals / Why are we doing this / What problem does this artifact solve / Which current state does it improve

- How can we get more human-made labels? --> Using Citizen Science to include the public with a collaborative, gamified interactive labeling approach.

## Requirements


1. As a labeler I want to label publications
   1. As a labeler, I expect the system to help me during labeling
      1. As a labeler, I want to understand why the model made a certain prediction
      2. As a labeler, I expect the system to provide me a type of guide (checklist), that explains when a SDG is generally fulfilled
         1. As a labeler, I want to drill-down for a more detailed guide for a specific SDG
   2. As a labeler, I want a personalized labeling experience
      1. As a labeler, I expect the system to suggest some labels that are tailored to my background and skills
      2. As a labeler, I expect the system to explain me those suggestions
   3. As a labeler, I want to receive feedback if my labeling suggestions were accurate
   4. As a labeler, I would like to communicate my thoughts, why I label a certain publications
   5. As a labeler, I expect particpating in a labeling environement that incorporates gamification
      1. As a labeler, I expect to see some form of local (labelerprofile-oriented) progress (ELO, XP, Coins, ...) when I'm actively participating in the labling process
   6. As a labeler, I want to see a summary of the clues from other users for a publcations
      1. As a labeler, I want to see other labelers suggestions on the labeled publication
      2. As a labeler, I want to see explanations from experts on the labeled publication
   7. As a labeler, I want to have a dashboard that initialized the labeling process
      1. As a labeler, I expect the dashboard to summarize my profile and my provious labeling performance in form of a history
      2. As a labeler, I expect the dashboard to provide some form of exploration for publications to be labeled
         1. As a labeler, I expect the exploration provide a bookmarking functionality to have an alternative for suggested publications
   8. As a labeler, I want to check my own performance
      1. As a labeler, I would like to compare my labeling performance with others by looking at the global leaderboard

2. As an expert, I want to oversee and manage the labling process
   1. As an expert, I want to label publications with minimal effort by accepting / rejecting labeler recommendations
   2. As an expert, I want to switch to the labeler role to label publications
   3. As an expert, I want a summary of the overall labeling progress of the community in a leaderboard-like manner
   4. As an expert, I want take influece on the distribution of non-labeled publications to optimize the overall labelig process in the community
   5. As an expert, I expect the system to streamline my workflow for accepting rejecting by providing guidance and recommendations
      1. As an expert, I expect the system to explain those recommendations

3. As an admin I want to orchestrate the labeling community and the labeling system
   1. As an admin, I want to mange the labelers system
      1. As an admin, I want to create, update and delete users
   2. As an admin, I want to mange the database system
   3. As an admin, I want to mange the datapipeline
      1. As an admin, I want to orchestrate the download / update of publications to the database
   4. As an admin, I want to fine-tune the models based on labels.
      1. As an admin, I want to trigger the model fine-tuning after collection enough labels
   5. As an admin, I want to manage the gamification parameters


Gamification aspects
- Personalization: Avatar
- Earn Rewards: ELO, XP, Coin system, Badges, Glyphe -> Progress
  - Glyph: Flower, we dont need to vis. all 17 sdgs, maybe only top3
- Show Rewards: Leaderboard
- Quests: Awareness / Microlearning, more rewards
- Incentive to label publications:
  - continue labeling even if it was wrong -> Result transparaney and feedbackloop
  - label publicaitons that will improve the most -> Result transparancey and Epic meaning


Roles:

- Labeler is a User
- Expert is a User and a Labeler
- Admin is a User


Routes:

``` md
/
├── login
├── dashboard (labeler)
│   ├── profile
│   ├── publications
│   │   ├── label
│   │   ├── explore
│   │   ├── bookmarks
│   │   └── :id
│   │       ├── label
│   │       ├── comments
│   │       └── expert-feedback
│   ├── leaderboard
│   └── quests
├── dashboard (expert)
│   ├── labeler-recommendations
│   │   └── :id
│   ├── community-progress
│   └── label-distribution
└── cockpit (admin)
    ├── user-management
    ├── database-management
    ├── datapipeline
    ├── model-management
    └── gamification-management
```

