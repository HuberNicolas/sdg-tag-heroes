<template>
  <nav class="w-full h-16 bg-white shadow-md flex items-center">
    <div v-if="loading" class="flex justify-center items-center w-full h-16">
      <Icon
        :name="loadingHexagon"
        class="w-10 h-10 text-gray-500 transition-all animate-pulse"
      />
      <span class="ml-2 text-gray-500">Loading...</span>
    </div>

    <div v-else class="w-full flex justify-between items-center px-1 py-1 flex-nowrap overflow-x-auto">
      <UModal v-model="isXPModalOpen">
        <div class="p-8 bg-white rounded-xl shadow-2xl flex flex-col items-center text-center space-y-6 max-w-2xl w-full animate-fade-in scale-105 relative">

          <!-- Large Community / Awareness Icon -->
          <div class="relative flex items-center justify-center">
            <Icon
              name="line-md:group"
              class="w-[160px] h-[160px] text-gray-600 opacity-10 absolute"
            />

            <!-- SDG Icon (Smaller) -->
            <div v-if="xpModalContent?.sdg" class="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center border-4 z-10" :style="{ borderColor: sdgModalColor }">
              <img
                :src="getSdgIconSrc(xpModalContent.sdg)"
                :alt="`SDG ${xpModalContent.sdg} Icon`"
                class="w-full h-full object-contain rounded-md"
              />
            </div>
          </div>

          <!-- Title -->
          <h2 v-if="xpModalContent?.title" class="text-3xl font-bold text-gray-900 relative z-10">
            {{ xpModalContent.title }}
          </h2>

          <!-- Contribution Message -->
          <h3 class="text-2xl font-semibold text-gray-800 relative z-10">
            Your Labeling Helps Build a Smarter & More Sustainable Future!
          </h3>

          <!-- XP Earned Description -->
          <p v-if="xpModalContent?.description" class="text-lg text-gray-700 leading-relaxed relative z-10">
            {{ xpModalContent.description }}
          </p>

          <!-- Additional Awareness / Community Message -->
          <p class="text-md text-gray-600 italic relative z-10">
            Through your participation, you're increasing <b>SDG awareness</b>, improving <b>AI training</b>, and empowering a <b>global community</b> of citizen scientists.
          </p>

          <!-- Player Rank Section -->
          <div v-if="playerRankData" class="flex flex-col items-center mt-4 relative z-10">
            <p class="text-lg font-semibold text-gray-800">
              Your Rank in SDG {{ xpModalContent?.sdg.replace('sdg', '') }}
            </p>

            <div class="flex items-center space-x-3 p-3 bg-gray-100 rounded-lg shadow-md">
              <Icon v-if="playerRankData.tier === 1" name="line-md:chevron-up" class="w-6 h-6" :style="{ color: sdgModalColor }" />
              <Icon v-else-if="playerRankData.tier === 2" name="line-md:chevron-double-up" class="w-6 h-6" :style="{ color: sdgModalColor }" />
              <Icon v-else-if="playerRankData.tier === 3" name="line-md:chevron-triple-up" class="w-6 h-6" :style="{ color: sdgModalColor }" />
              <Icon v-else name="line-md:minus" class="w-6 h-6 text-gray-400" />

              <span class="px-3 py-1 rounded-lg text-white text-sm font-semibold" :style="{ backgroundColor: sdgModalColor }">
          {{ playerRankData.name }}
        </span>

              <span class="text-lg font-semibold text-gray-800">
          Tier {{ playerRankData.tier }}
        </span>
            </div>
          </div>

          <!-- XP Earned Display -->
          <div v-if="xpModalContent?.increment" class="flex flex-col items-center mt-4 relative z-10">
            <p class="text-lg font-semibold text-gray-800">Experience Points Earned</p>
            <span class="text-2xl font-bold" :style="{ color: sdgModalColor }">
        {{ Math.round(xpModalContent.increment) }} XP
      </span>
          </div>

          <!-- Progress Bar Chart -->
          <ProgressBarChart
            v-if="xpModalContent?.sdg && playerRankData"
            :currentXp="Math.round(xpModalContent.xp)"
            :nextLevelXp="getNextLevelXp(xpModalContent.sdg, playerRankData.tier)"
            :sdgColor="sdgModalColor"
            class="relative z-10"
          />

          <!-- Closing Note -->
          <p class="text-sm text-gray-500 italic relative z-10">
            Your contributions fuel AI-driven sustainability efforts while rewarding you with knowledge & recognition!
          </p>

          <!-- Close Button -->
          <UButton
            label="Keep Going!"
            class="px-8 py-3 text-white text-lg font-semibold rounded-lg hover:bg-opacity-80 transition-all relative z-10"
            :style="{ backgroundColor: sdgModalColor }"
            @click="closeXPModal"
          />
        </div>
      </UModal>


      <UModal v-model="isCoinModalOpen">
        <div class="p-8 bg-white rounded-xl shadow-2xl flex flex-col items-center text-center space-y-6 max-w-2xl w-full animate-fade-in scale-105 relative">

          <!-- Title -->
          <h2 v-if="coinModalContent?.title" class="text-3xl font-bold text-gray-900 relative z-10 mb-4">
            {{ coinModalContent.title }}
          </h2>

          <!-- Large Publication Icon (Now wrapping SDG Icon) -->
          <div class="relative flex items-center justify-center p-4">
            <Icon
              name="line-md:document"
              class="w-[200px] h-[200px] text-gray-600 opacity-10 absolute"
            />

            <!-- SDG Icon (Smaller) -->
            <div v-if="coinModalContent?.sdg" class="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center border-4 z-10" :style="{ borderColor: sdgColor }">
              <img
                :src="getSdgIconSrc(coinModalContent.sdg)"
                :alt="`SDG ${coinModalContent.sdg} Icon`"
                class="w-full h-full object-contain rounded-md"
              />
            </div>
          </div>



          <!-- Contribution Message -->
          <h3 v-if="coinModalContent?.title" class="text-2xl font-semibold text-gray-800 relative z-10">
            Your Contribution Makes a Difference!
          </h3>

          <!-- Coin Earned Description -->
          <p v-if="coinModalContent?.description" class="text-lg text-gray-700 leading-relaxed relative z-10">
            {{ coinModalContent.description }}
          </p>

          <!-- Additional Value Proposition -->
          <p class="text-md text-gray-600 italic relative z-10">
            By participating in labeling, you helped train AI models and advance scientific research while earning rewards!
          </p>

          <!-- Coins Earned Display -->
          <div v-if="coinModalContent?.increment" class="flex flex-col items-center mt-4 relative z-10">
            <p class="text-lg font-semibold">Coins Earned</p>
            <span class="text-2xl font-bold" :style="{ color: sdgModalColor }">
        {{ Math.round(coinModalContent.increment) }} Coins
      </span>
          </div>

          <!-- Closing Note -->
          <p class="text-sm text-gray-500 italic relative z-10">
            Keep labeling and earning—your contributions fuel AI training & SDG research!
          </p>

          <!-- Close Button -->
          <UButton
            label="Awesome!"
            class="px-8 py-3 text-white text-lg font-semibold rounded-lg hover:bg-opacity-80 transition-all relative z-10"
            :style="{ backgroundColor: sdgModalColor }"
            @click="closeCoinModal"
          />
        </div>
      </UModal>



      <div class="flex items-center space-x-6">
        <NuxtLink
          v-for="(link, index) in links.slice(0, 1)"
          :key="index"
          :to="link.to || '#'"
          class="flex items-center space-x-2 text-sm font-medium text-gray-700 hover:text-primary"
        >
          <component :is="link.icon" class="w-5 h-5" v-if="typeof link.icon === 'string'" />
          <component :is="link.icon" v-else class="w-5 h-5" />
          <span>{{ link.label }}</span>
        </NuxtLink>
    </div>

      <!-- World Display -->
      <div v-if="gameStore.getSDG" class="flex items-center space-x-4">
        <span>World:</span>
        <div class="w-8 h-8 flex items-center justify-center">
          <img
            :src="sdgIconSrc"
            :alt="`SDG ${gameStore.getSDG} Icon`"
            class="w-full h-full object-contain"
          />
        </div>
      </div>

      <!-- Level Display -->
      <div v-if="gameStore.getLevel" class="flex items-center space-x-4">
        <span>Level:</span>
        <div class="flex items-end space-x-1">
          <!-- Render podium steps based on the level -->
          <template v-if="gameStore.getLevel === 1">
            <UIcon name="mdi-signal-cellular-1" class="w-10 h-10" :style="{ color: sdgColor }" />
          </template>
          <template v-else-if="gameStore.getLevel === 2">
            <UIcon name="mdi-signal-cellular-2" class="w-10 h-10" :style="{ color: sdgColor }" />
          </template>
          <template v-else-if="gameStore.getLevel === 3">
            <UIcon name="mdi-signal-cellular-3" class="w-10 h-10" :style="{ color: sdgColor }" />
          </template>
        </div>
        <!--        <span
          class="px-3 py-1 rounded-md border font-semibold"
          :class="getLevelClass(gameStore.getLevel)"
        >
    {{ getRomanLevel(gameStore.getLevel) }}
        </span> -->
      </div>

      <div class="flex items-center space-x-4">
        <span>Stage:</span>
        <span class="font-semibold">
          <template v-if="gameStore.getStage === 'Exploring'">
            <Icon name="mdi-person-search" /> {{ gameStore.getStage }}
          </template>
          <template v-else-if="gameStore.getStage === 'Labeling'">
            <Icon name="mdi-tag-outline" /> {{ gameStore.getStage }}
          </template>
          <template v-else-if="gameStore.getStage === 'Voting'">
            <Icon name="mdi-vote" /> {{ gameStore.getStage }}
          </template>
          <template v-else>
            {{ gameStore.getStage }}
          </template>
        </span>
      </div>

      <!-- Quadrant Display -->
      <div v-if="gameStore.getQuadrant!== null" class="flex items-center space-x-4">
        <span>Situation:</span>
        <!-- Render only the active quadrant -->
        <div class="p-1 border rounded-md w-10 h-10 text-xs flex flex-col items-center justify-between">

          <!-- Many Publications, All SDGs -->
          <template v-if="gameStore.getQuadrant === Quadrant.MANY_PUBS_ALL_SDG">
            <div class="flex space-x-0.5">
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
            </div>
            <div class="flex space-x-0.5">
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
            </div>
          </template>

          <!-- Many Publications, 1 SDG -->
          <template v-if="gameStore.getQuadrant === Quadrant.MANY_PUBS_ONE_SDG">
            <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
            <div class="flex space-x-0.5">
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
              <Icon name="line-md-document" class="w-3 h-3 text-gray-600"/>
            </div>
          </template>

          <!-- 1 Publication, All SDGs -->
          <template v-if="gameStore.getQuadrant === Quadrant.ONE_PUB_ALL_SDG">
            <div class="flex space-x-0.5">
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
              <Icon name="ph-hexagon-light" class="w-3 h-3 text-gray-600"/>
            </div>
            <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
          </template>

          <!-- 1 Publication, 1 SDG -->
          <template v-if="gameStore.getQuadrant === Quadrant.ONE_PUB_ONE_SDG">
            <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
            <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
          </template>
        </div>
      </div>

      <div
        v-for="(link, index) in links.slice(1, 3)"
        :key="index"
        class="flex items-center space-x-2 text-sm font-medium text-gray-700"
      >
        <span>{{ link.label }}</span>
      </div>

      <div>Your Top SDGs:</div>
      <div
        v-for="(link, index) in links.slice(3)"
        :key="index"
        class="flex flex-col items-center space-y-1"
      >
        <NuxtLink :to="{ path: `/exploration/sdgs/${link.to}/1` }">
          <!-- Dynamic SDG Icon -->
          <!-- Title -->
          <div class="w-8 h-8 flex items-center justify-center">
            <img
              v-if="link.icon"
              :src="`data:image/svg+xml;base64,${link.icon}`"
              :alt="`SDG ${index + 1} Icon`"
              class="w-full h-full object-contain"
            />
          </div>

          <!-- Label -->
          <span class="text-xs font-medium text-gray-600">
              {{ link.label }}
            </span>
        </NuxtLink>
      </div>

      <!-- Right Section: Avatar -->
      <div class="flex items-center space-x-6">

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <span v-if="currentRank" class="font-semibold text-gray-700 whitespace-nowrap">
            {{ currentRank.name }}
          </span>
        </div>

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <span v-if="currentRank" class="text-sm text-gray-500 whitespace-nowrap">
            Tier {{ currentRank.tier }}
          </span>
        </div>

        <div v-if="gameStore.getSDG" class="flex flex-col items-start ml-4">
          <!-- Rank Symbol (Chevron Icons) -->
          <Icon
            v-if="currentRank?.tier === 1"
            name="line-md:chevron-up"
            :style="{ color: sdgColor }"
            class="w-6 h-6"
          />
          <Icon
            v-else-if="currentRank?.tier === 2"
            name="line-md:chevron-double-up"
            :style="{ color: sdgColor }"
            class="w-6 h-6"
          />
          <Icon
            v-else-if="currentRank?.tier === 3"
            name="line-md:chevron-triple-up"
            :style="{ color: sdgColor }"
            class="w-6 h-6"
          />
          <Icon v-else name="line-md:minus" class="text-gray-400 w-6 h-6" />
        </div>

        <NuxtLink :to="{ path: `/users/${userStore.getCurrentUser?.userId}`}"  class="flex items-center space-x-2">
          <div class="user-avatar">
            <UAvatar
              v-if="userStore.getCurrentUser?.email"
              size="sm"
              :src="generateAvatar(userStore.getCurrentUser.email)"
              alt="Avatar"
            />
            <div v-else class="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center">
              <span class="text-gray-500">No Avatar</span>
            </div>
          </div>
        </NuxtLink>

        <div class="drawer drawer-end z-10">
          <input id="drawer-help" type="checkbox" class="drawer-toggle hidden" />
          <div class="drawer-content">
            <UButton size="sm" color="primary" variant="solid" onclick="document.getElementById('drawer-help').checked = true;">
              Help
            </UButton>
          </div>

          <div class="drawer-side">
            <label for="drawer-help" aria-label="close sidebar" class="drawer-overlay"></label>

            <div class="menu bg-base-200 text-base-content min-h-full w-1/5 p-4 flex flex-col items-center">
              <UDivider label="SDG Cheatsheet" size="xl" />
              <SDGSelectorHelp></SDGSelectorHelp>
              <UDivider label="How to Label" size="xl" />
              <div class="flex flex-col gap-1.5 p-3 border rounded-lg bg-gray-50 text-sm w-full">
                <h3 class="font-semibold text-gray-700 flex items-center gap-1.5">
                  <Icon name="mdi-scale-balance" class="w-4 h-4 text-gray-500" /> How to Decide
                </h3>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-book-open-variant" class="w-4 h-4 text-gray-500" />
                  <span>Check title & abstract</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-earth" class="w-4 h-4 text-gray-500" />
                  <span>Does it help people or nature?</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-lightbulb-on-outline" class="w-4 h-4 text-gray-500" />
                  <span>AI suggests SDGs</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-account-group" class="w-4 h-4 text-gray-500" />
                  <span>See community labels</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-check-circle-outline" class="w-4 h-4 text-gray-500" />
                  <span><b>Yes</b> → Clear SDG link</span>
                </div>

                <div class="flex items-center gap-1.5">
                  <Icon name="mdi-close-circle-outline" class="w-4 h-4 text-gray-500" />
                  <span><b>No</b> → Unclear or unrelated</span>
                </div>
              </div>
              <!-- <h1 class="text-lg font-bold mb-4 text-center w-full">Situations</h1> -->
              <UDivider label="Situations" size="xl" />
              <div class="flex flex-col gap-4 p-4 bg-gray-50 border rounded-md text-sm">

                <!-- Context Overview -->
                <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                  <Icon name="ph-map-light" class="w-6 h-6 text-gray-700 mb-2" />
                  <h3 class="font-semibold text-gray-700">How It Works</h3>
                  <p class="text-gray-600">
                    Start in an exploration space with many publications and SDGs.
                    Your goal is to <b>drill down step-by-step</b> until you reach a single publication that can be labeled.
                    There are <b>multiple paths</b> possible.
                  </p>
                </div>

                <!-- Decide the Game Mode -->
                <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                  <Icon name="ph-map-light" class="w-6 h-6 text-gray-700 mb-2" />
                  <h3 class="font-semibold text-gray-700">Different Game Modes</h3>
                  <p class="text-gray-600">
                    You can decide between two game modes: Game Mode <b>SDG Specialization</b> and Game Mode <b>Open World Exploration</b>
                  </p>
                </div>

                <!-- Two Main Paths: SDG Specialization vs. Open World -->
                <div class="grid grid-cols-2 gap-4">

                  <!-- Scenario 1: SDG Specialization -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                    <Icon name="ph-target-light" class="w-6 h-6 text-gray-700 mb-2" />
                    <h3 class="font-semibold text-gray-700"><b>SDG Specialization</b></h3>
                    <p class="text-gray-600">Choose <b>one specific SDG</b> and focus only on publications relevant to that goal.</p>
                  </div>

                  <!-- Scenario 2: Open World Exploration -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                    <Icon name="ph-globe-light" class="w-6 h-6 text-gray-700 mb-2" />
                    <h3 class="font-semibold text-gray-700"><b>Open World Exploration</b></h3>
                    <p class="text-gray-600">Browse freely across <b>all SDGs</b>, discovering broader research connections.</p>
                  </div>

                  <!-- Many Publications, One SDG -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                    <Icon name="ph-list-light" class="w-6 h-6 text-gray-700 mb-2" />
                    <h3 class="font-semibold text-gray-700">Focused Search</h3>
                    <p class="text-gray-600">Drill down into a single SDG, filtering out publications that are unrelated.</p>
                  </div>

                  <!-- Many Publications, All SDGs -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                    <Icon name="ph-stack-light" class="w-6 h-6 text-gray-700 mb-2" />
                    <h3 class="font-semibold text-gray-700">Broad Overview</h3>
                    <p class="text-gray-600">Analyze a wide set of publications across all SDGs to identify patterns and trends.</p>
                  </div>

                  <!-- One Publication, One SDG -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                    <Icon name="ph-check-circle-light" class="w-6 h-6 text-gray-700 mb-2" />
                    <h3 class="font-semibold text-gray-700">Final Labeling</h3>
                    <p class="text-gray-600">You’ve reached a single publication. Now it’s time to make the final SDG decision.</p>
                  </div>


                  <!-- One Publication, All SDGs -->
                  <div class="flex flex-col items-center text-center p-3 border rounded-md bg-white shadow">
                    <Icon name="ph-books-light" class="w-6 h-6 text-gray-700 mb-2" />
                    <h3 class="font-semibold text-gray-700">Multi-SDG Impact</h3>
                    <p class="text-gray-600">Examine a single publication and determine if it contributes to any of the SDGs.</p>
                  </div>

                </div>


              </div>


              <div class="grid grid-flow-col grid-cols-3 grid-rows-3 gap-4 w-80 h-80 border border-gray-300 bg-white p-2 rounded-md">

                <div class="col-span-1 row-span-1flex flex-col items-center justify-center bg-white text-black font-bold p-2 rounded-md">
                </div>

                <!-- Publications Label (Y-axis, Vertical) -->
                <div class="row-span-2 flex flex-col items-center justify-center text-black font-bold p-2 rounded-md">
                  <span class="transform rotate-180 whitespace-nowrap [writing-mode:vertical-lr]">Publications (N - 1)</span>
                  <Icon name="line-md-document" class="w-5 h-5 text-black mt-1"/>
                </div>

                <!-- SDGs Label (X-axis) -->
                <div class="col-span-2 flex flex-col items-center justify-center text-black font-bold p-2 rounded-md">
                  <span>SDGs (17 - 1)</span>
                  <Icon name="ph-hexagon-light" class="w-5 h-5 text-black mt-1"/>
                </div>

                <!-- Quadrant: Many Publications, All SDGs -->
                <UTooltip text="Many Publications, All SDGs" :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center border border-gray-300 rounded-md shadow-md w-full h-full"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.MANY_PUBS_ALL_SDG }">

                    <div class="flex space-x-1">
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                    </div>

                    <div class="flex space-x-1 mt-1">
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                    </div>
                  </div>
                </UTooltip>



                <!-- Quadrant: 1 Publication, All SDGs -->
                <UTooltip text="One Publication, All SDGs" :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center  border border-gray-300 rounded-md shadow-md w-full h-full"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.ONE_PUB_ALL_SDG }">
                    <div class="flex space-x-1">
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                      <Icon name="ph-hexagon-light" class="w-4 h-4 text-gray-600"/>
                    </div>
                    <Icon name="line-md-document" class="w-5 h-5 text-gray-600 mt-1"/>
                  </div>
                </UTooltip>

                <!-- Quadrant: Many Publications, 1 SDG -->
                <UTooltip text="Many Publications, One SDG" :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center border border-gray-300 rounded-md shadow-md w-full h-full"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.MANY_PUBS_ONE_SDG }">
                    <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
                    <div class="flex space-x-1 mt-1">
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                      <Icon name="line-md-document" class="w-4 h-4 text-gray-600"/>
                    </div>
                  </div>
                </UTooltip>

                <!-- Quadrant: 1 Publication, 1 SDG -->
                <UTooltip text="One Publication, One SDG" :popper="{ strategy: 'absolute', placement: 'top', arrow: true }">
                  <div class="col-span-1 row-span-1 flex flex-col items-center justify-center border border-gray-300 rounded-md shadow-md w-full h-full"
                       :class="{ 'bg-gray-300': gameStore.getQuadrant === Quadrant.ONE_PUB_ONE_SDG }">
                    <Icon name="ph-hexagon-light" class="w-4 h-4" :style="{ color: sdgColor }"/>
                    <Icon name="line-md-document" class="w-5 h-5 text-gray-600 mt-1"/>
                  </div>
                </UTooltip>
              </div>


            </div>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { onMounted, ref, watchEffect } from "vue";
import { useUsersStore } from "~/stores/users";
import { useXPBanksStore } from "~/stores/xpBanks";
import { useCoinWalletsStore } from "~/stores/coinWallets";
import { useSDGsStore } from "~/stores/sdgs";
import { useGameStore } from "~/stores/game";
import { useSDGRanksStore } from "~/stores/sdgRanks";
import { generateAvatar } from "~/utils/avatar";
import { Quadrant } from "~/types/enums";
import { usePublicationsStore } from "~/stores/publications";

const publicationsStore = usePublicationsStore();

const getPublicationTitle = async (publicationId: number): Promise<string> => {
  try {
    const publication = await publicationsStore.fetchPublicationWithoutStoreById(publicationId);
    return publication?.title || "Unknown Publication";
  } catch (error) {
    console.error(`Failed to fetch publication title: ${error}`);
    return "Unknown Publication";
  }
};

// Pinia stores
const userStore = useUsersStore();
const banksStore = useXPBanksStore();
const walletsStore = useCoinWalletsStore();
const sdgsStore = useSDGsStore();
const gameStore = useGameStore();
const rankStore = useSDGRanksStore();

// State
const loading = ref(true);
const links = ref<Array<any>>([]);


//const isOpen = ref(false);
//const modalContent = ref<{ title: string; description: string; xp?: number; increment?: number; sdg?: SDGType; publicationTitle?: string } | null>(null);

const isXPModalOpen = ref(false);
const isCoinModalOpen = ref(false);

const xpModalContent = ref<{ title: string; description: string; xp?: number; increment?: number; sdg?: SDGType; publicationTitle?: string } | null>(null);
const coinModalContent = ref<{ title: string; description: string; increment?: number; sdg?: SDGType; publicationTitle?: string } | null>(null);

const playerRankData = ref<{ name: string; tier: number } | null>(null);

const openXPModal = ({ title, description, sdg, publicationTitle, playerRank, increment, xp = 0 }) => {
  xpModalContent.value = {
    title,
    description,
    sdg,
    publicationTitle,
    increment,
    xp,
  };

  isXPModalOpen.value = true;
};

const openCoinModal = ({ title, description, sdg, publicationTitle, playerRank, increment }) => {
  coinModalContent.value = {
    title,
    description,
    sdg,
    publicationTitle,
    increment,
  };

  // Open Coin modal only after XP modal closes
  if (isXPModalOpen.value) {
    setTimeout(() => {
      isCoinModalOpen.value = true;
    }, 3000);
  } else {
    isCoinModalOpen.value = true;
  }
};

const closeXPModal = () => {
  isXPModalOpen.value = false;
  xpModalContent.value = null;

  // Ensure XP modal is fully closed before opening Coin modal
  setTimeout(() => {
    if (!isXPModalOpen.value && coinModalContent.value) {
      isCoinModalOpen.value = true;
    }
  }, 3000); // Small delay to allow modal transition
};

const closeCoinModal = () => {
  isCoinModalOpen.value = false;
  coinModalContent.value = null;
};


const checkUpdates = async () => {
  try {
    await banksStore.fetchLatestXPBankHistory();
    await banksStore.fetchPersonalXPBank();
    const latestXP = banksStore.latestXPBankHistory;

    if (latestXP && latestXP.increment) {
      const publicationId = extractPublicationId(latestXP.reason || "");
      const publicationTitle = publicationId ? await getPublicationTitle(publicationId) : "Unknown Publication";
      const playerRank = getPlayerRank(userStore.getCurrentUser?.userId, latestXP.sdg);
      playerRankData.value = playerRank; // Ensure this is properly set

      const xpForSdg = banksStore.userXPBank ? banksStore.userXPBank[`${latestXP.sdg}Xp`] : 0;

      openXPModal({
        title: `XP Earned!`,
        description: `You earned ${latestXP.increment} XP for labeling the publication: "${publicationTitle}".`,
        publicationTitle,
        sdg: latestXP.sdg,
        playerRank,
        increment: latestXP.increment,
        xp: xpForSdg,
      });


    }
  } catch (error) {
    console.error("Failed to fetch latest XP update", error);
  }

  try {
    await walletsStore.fetchLatestSDGCoinWalletHistory();
    await banksStore.getUserXPBank;
    const latestWallet = walletsStore.latestSDGCoinWalletHistory;

    if (latestWallet && latestWallet.increment) {
      const publicationId = extractPublicationId(latestWallet.reason || "");
      const publicationTitle = publicationId ? await getPublicationTitle(publicationId) : "Unknown Publication";

      const sdg = extractSDGFromReason(latestWallet.reason || "");
      const playerRank = getPlayerRank(userStore.getCurrentUser?.userId, sdg);
      const coinsForSdg = walletsStore.userSDGCoinWallet ? walletsStore.userSDGCoinWallet[`${sdg}Coins`] : 0;
      // Open the coins-earned modal after the XP modal if both exist
      setTimeout(() => {
        openCoinModal({
          title: `Coins Earned!`,
          description: `You earned ${latestWallet.increment} SDG Coins for the publication: "${publicationTitle}".`,
          publicationTitle,
          sdg,
          playerRank,
          increment: latestWallet.increment,
          coins: coinsForSdg,
        });
      }, isXPModalOpen.value ? 3000 : 0); // Delay if XP modal is still open
    }
  } catch (error) {
    console.error("Failed to fetch latest wallet update", error);
  }
};




const fetchData = async () => {
  try {
    // First fetch the user data
    await userStore.fetchPersonalUser();

    // Then fetch all other data in parallel
    await Promise.all([
      walletsStore.fetchPersonalSDGCoinWallet(),
      banksStore.fetchPersonalXPBank(),
      sdgsStore.fetchSDGs(),
      rankStore.fetchSDGRankByUserId(userStore.getCurrentUser?.userId || 0),
      rankStore.fetchSDGRanks()
    ]);

    const user = userStore.getCurrentUser;
    const userWallet = walletsStore.getUserSDGCoinWallet;
    const userBank = banksStore.getUserXPBank;

    // Update links with fetched data
    updateLinks(userWallet?.totalCoins || 0, userBank || { totalXp: 0 });
  } catch (error) {
    console.error('Error fetching user data:', error);
    updateLinks(0, { totalXp: 0 }); // Fallback values
  } finally {
    loading.value = false;
  }
};

// Update links with user data
const updateLinks = (coins: number, xpData: any) => {
  const { totalXp, ...sdgXpFields } = xpData;

  const top3SDGs = Object.entries(sdgXpFields)
    .filter(([key]) => key.startsWith('sdg') && key.endsWith('Xp'))
    .map(([key, xp]) => {
      const normalizedKey = key.replace('Xp', '');
      const sdgId = parseInt(normalizedKey.replace('sdg', ''), 10);
      const sdg = sdgsStore.sdgs.find((s) => s.id === sdgId);
      return {
        sdg: normalizedKey,
        xp: xp as number,
        icon: sdg?.icon,
        to: `${sdgId}`,
      };
    })
    .sort((a, b) => b.xp - a.xp)
    .slice(0, 3)
    .map((sdgData) => ({
      label: `${sdgData.xp.toFixed(0)} XP`,
      icon: sdgData.icon,
      to: sdgData.to,
    }));

  links.value = [
    { label: 'Game Mode', to: '/scenarios' },
    { label: `Total SDG XP: ${totalXp.toFixed(0)}` },
    { label: `SDG Coins: ${coins.toFixed(0)}` },
    ...top3SDGs,
  ];
};

const currentRank = computed(() => {
  if (!gameStore.getSDG || !rankStore.userSDGRank) return null;

  return rankStore.userSDGRank.find(
    rank => rank.sdgGoalId === gameStore.getSDG
  ) || rankStore.userSDGRank[0];
});

// Get the currently selected SDG
const currentSDG = computed(() => {
  const sdgId = gameStore.getSDG;
  return sdgsStore.sdgs.find((sdg) => sdg.id === sdgId) || null;
});

// Computed property to get the color of the selected SDG
const sdgColor = computed(() => {
  return currentSDG.value ? sdgsStore.getColorBySDG(currentSDG.value.id) : "#A0A0A0"; // Default gray if no SDG
});

// Convert level to Roman numerals
const getRomanLevel = (level: number | null) => {
  if (level === null) return "N/A";
  const romanNumerals = ["I", "II", "III"];
  return level > 0 && level <= 10 ? romanNumerals[level - 1] : level;
};

// Assign tier color based on level
const getLevelClass = (level: number | null) => {
  if (level === 1) return "bg-orange-200 border-orange-400 text-orange-800"; // Bronze
  if (level === 2) return "bg-gray-200 border-gray-400 text-gray-700"; // Silver
  if (level === 3) return "bg-yellow-200 border-yellow-500 text-yellow-800"; // Gold
  else return "bg-gray-200 border-gray-400 text-gray-700";
};

const sdgIconSrc = computed(() => {
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === gameStore.getSDG);
  return `data:image/svg+xml;base64,${sdg.icon}`;
});

const getSdgIconSrc = (sdgType: SDGType) => {
  // Extract the numeric ID from the SDGType string (e.g., "sdg1" -> 1, "sdg13" -> 13)
  const sdgId = parseInt(sdgType.replace('sdg', ''), 10);

  // Find the SDG object in the store using the numeric ID
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === sdgId);

  // Return the base64-encoded SVG icon if found
  return sdg ? `data:image/svg+xml;base64,${sdg.icon}` : null;
};

const extractPublicationId = (reason: string): number | null => {
  const match = reason.match(/Publication (\d+)/);
  return match ? parseInt(match[1], 10) : null;
};

const getPlayerRank = (userId: number, sdgType: SDGType) => {
  const sdgId = parseInt(sdgType.replace("sdg", ""), 10);
  const userRankData = rankStore.userSDGRanks.find((u) => u.userId === userId);
  const rank = userRankData?.ranks.find((r) => r.sdgGoalId === sdgId);

  return rank ? { name: rank.name, tier: rank.tier } : { name: "No Rank", tier: 0 };
};

const sdgModalColor = computed(() => {
  if (!xpModalContent.value?.sdg) return "#A0A0A0"; // Default gray if no SDG selected

  const sdgId = parseInt(xpModalContent.value.sdg.replace("sdg", ""), 10);
  const sdg = sdgsStore.sdgs.find(sdg => sdg.id === sdgId);

  return sdg ? sdgsStore.getColorBySDG(sdg.id) : "#A0A0A0"; // Use fallback gray if SDG not found
});

// Function to get the XP required for the next level
const getNextLevelXp = (sdgType: string, currentTier: number) => {
  const sdgKey = `sdg_${sdgType.replace('sdg', '')}`;
  const nextTier = currentTier + 1;
  const nextTierKey = `tier_${nextTier}`;

  const sdgData = rankStore.sdgLevels[sdgKey];
  if (sdgData && sdgData[nextTierKey]) {
    return sdgData[nextTierKey].xp_required;
  }
  return 0; // If max level, return 0 or handle accordingly
};

const extractSDGFromReason = (reason: string): string | null => {
  const match = reason.match(/SDG (\d+)/);
  return match ? `sdg${match[1]}` : null;
};


watchEffect(() => {
  if (!loading.value) {
    const userWallet = walletsStore.getUserSDGCoinWallet;
    const userBank = banksStore.getUserXPBank;
    updateLinks(userWallet?.totalCoins || 0, userBank || { totalXp: 0 });
  }
});

const hexagonStages = [
  "mdi:hexagon-slice-1",
  "mdi:hexagon-slice-2",
  "mdi:hexagon-slice-3",
  "mdi:hexagon-slice-4",
  "mdi:hexagon-slice-5",
  "mdi:hexagon-slice-6",
];

const loadingHexagon = ref("mdi:hexagon-slice-1");

onMounted(() => {

  let index = 0;
  setInterval(() => {
    loadingHexagon.value = hexagonStages[index];
    index = (index + 1) % hexagonStages.length;
  }, 500); // Change every 500ms

  fetchData();
  setInterval(() => {
    checkUpdates();
  }, 10000); // Check every minute
});
</script>
