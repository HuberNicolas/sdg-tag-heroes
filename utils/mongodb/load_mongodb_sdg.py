import base64
import os
from db.mongodb_connector import client

from settings.settings import MongoDBSDGSettings

mongodb_sdg_settings = MongoDBSDGSettings()


def encode_svg_to_base64(svg_path):
    with open(svg_path, "rb") as svg_file:
        encoded_svg = base64.b64encode(svg_file.read()).decode(mongodb_sdg_settings.SVG_ENCODING)
    return encoded_svg

def get_goal_svg_path(goal_index):
    svg_path_template = mongodb_sdg_settings.GOAL_SVG_PATH_TEMPLATE
    svg_path = svg_path_template.format(goal_index=goal_index)
    if os.path.exists(svg_path):
        return svg_path
    return None


# Define the database name
db_name = mongodb_sdg_settings.DB_NAME

# Check if the database exists and drop it if it does
if db_name in client.list_database_names():
    client.drop_database(db_name)
    print(f"Database '{db_name}' has been deleted.")

# Create a new connection to the database
db = client[db_name]


goals_collection = db.goals
targets_collection = db.targets

goal_data = [
    {'index': 1, 'name': "No Poverty", 'color': "#E5243B"},
    {'index': 2, 'name': "Zero Hunger", 'color': "#DDA83A"},
    {'index': 3, 'name': "Good Health", 'color': "#4C9F38"},
    {'index': 4, 'name': "Quality Education", 'color': "#C5192D"},
    {'index': 5, 'name': "Gender Equality", 'color': "#FF3A21"},
    {'index': 6, 'name': "Clean Water and Sanitation", 'color': "#26BDE2"},
    {'index': 7, 'name': "Affordable and Clean Energy", 'color': "#FCC30B"},
    {'index': 8, 'name': "Decent Work and Economic Growth", 'color': "#A21942"},
    {'index': 9, 'name': "Industry, Innovation and Infrastructure", 'color': "#FD6925"},
    {'index': 10, 'name': "Reduced Inequalities", 'color': "#DD1367"},
    {'index': 11, 'name': "Sustainable Cities and Communities", 'color': "#FD9D24"},
    {'index': 12, 'name': "Responsible Consumption and Production", 'color': "#BF8B2E"},
    {'index': 13, 'name': "Climate Action", 'color': "#3F7E44"},
    {'index': 14, 'name': "Life Below Water", 'color': "#0A97D9"},
    {'index': 15, 'name': "Life on Land", 'color': "#56C02B"},
    {'index': 16, 'name': "Peace, Justice and Strong Institutions", 'color': "#00689D"},
    {'index': 17, 'name': "Partnerships for the Goals", 'color': "#19486A"}
]

# Automatically add the encoded SVG icon for each goal
for goal in goal_data:
    svg_path = get_goal_svg_path(goal['index'])
    if svg_path:
        goal['icon'] = encode_svg_to_base64(svg_path)
    else:
        goal['icon'] = None  # Handle missing SVG files as needed

target_indices = {
    1: ["1.1", "1.2", "1.3", "1.4", "1.5", "1.a", "1.b"],
    2: ["2.1", "2.2", "2.3", "2.4", "2.5", "2.a", "2.b", "2.c"],
    3: ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.a", "3.b", "3.c", "3.d"],
    4: ["4.1", "4.2", "4.3", "4.4", "4.5", "4.6", "4.7", "4.a", "4.b", "4.c"],
    5: ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.a", "5.b", "5.c"],
    6: ["6.1", "6.2", "6.3", "6.4", "6.5", "6.6", "6.a", "6.b"],
    7: ["7.1", "7.2", "7.3", "7.a", "7.b"],
    8: ["8.1", "8.2", "8.3", "8.4", "8.5", "8.6", "8.7", "8.8", "8.9", "8.10", "8.a", "8.b"],
    9: ["9.1", "9.2", "9.3", "9.4", "9.5", "9.a", "9.b", "9.c"],
    10: ["10.1", "10.2", "10.3", "10.4", "10.5", "10.6", "10.7", "10.a", "10.b", "10.c"],
    11: ["11.1", "11.2", "11.3", "11.4", "11.5", "11.6", "11.7", "11.a", "11.b", "11.c"],
    12: ["12.1", "12.2", "12.3", "12.4", "12.5", "12.6", "12.7", "12.8", "12.a", "12.b", "12.c"],
    13: ["13.1", "13.2", "13.3", "13.a", "13.b"],
    14: ["14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7", "14.a", "14.b", "14.c"],
    15: ["15.1", "15.2", "15.3", "15.4", "15.5", "15.6", "15.7", "15.8", "15.9", "15.a", "15.b", "15.c"],
    16: ["16.1", "16.2", "16.3", "16.4", "16.5", "16.6", "16.7", "16.8", "16.9", "16.10", "16.a", "16.b"],
    17: ["17.1", "17.2", "17.3", "17.4", "17.5", "17.6", "17.7", "17.8", "17.9", "17.10", "17.11", "17.12", "17.13", "17.14", "17.15", "17.16", "17.17", "17.18", "17.19"]
}

target_texts = {
    1: ["Eradicate Extreme Poverty", "Reduce Poverty By At Least 50%", "Implement Social Protection Systems", "Equal Rights to Ownership, Basic Services, Technology and Economic Resources", "Build Resilience to Environmental, Economic and Social Disasters", "Mobilize Resources to Implement Policies to End Poverty", "Create Pro-Poor and Gender-Sensitive Policy Frameworks"],
    2: ["Universal Access to Safe and Nutritious Food", "End All Forms of Malnutrition", "Double the Productivity and Incomes of Small-Scale Food Producers", "Sustainable Food Production And Resilient Agricultural Practices", "Maintain the Genetic Diversity in Food Production", "Invest in Rural Infrastructure, Agricultural Research, Technology and Gene Banks", "Prevent Agricultural Trade Restrictions, Market Distortions and Export Subsidies", "Ensure Stable Food Commodity Markets and Timely Access to Market Information"],
    3: ["Reduce Maternal Mortality", "End All Preventable Deaths Under 5 Years of Age", "Fight Communicable Diseases", "Reduce Mortality From Non-Communicable Diseases and Promote Mental Health", "Prevent and Treat Substance Abuse", "Reduce Road Injuries and Deaths", "Universal Access to Sexual and Reproductive Care, Family Planning and Education", "Achieve Universal Health Coverage", "Reduce Illnesses and Death from Hazardous Chemicals and Pollution", "Implement the Who Framework Convention on Tobacco Control", "Support Research, Development and Universal Access to Affordable Vaccines and Medicines", "Increase Health Financing and Support Health Workforce in Developing", "Improve Early Warning Systems for Global Health Risks"],
    4: ["Free Primary and Secondary Education", "Equal Access to Quality Pre-Primary Education", "Equal Access to Affordable Technical, Vocational and Higher Education", "Increase the Number of People with Relevant Skills for Financial Success", "Eliminate All Discrimination in Education", "Universal Literacy and Numeracy", "Education for Sustainable Development and Global Citizenship", "Build and Upgrade Inclusive and Safe Schools", "Expand Higher Education Scholarships for Developing Countries", "Increase the Supply of Qualified Teachers in Developing Countries"],
    5: ["End Discrimination Against Women and Girls", "End All Violence Against And Exploitation of Women and Girls", "Eliminate Forced Marriages and Genital Mutilation", "Value Unpaid Care and Promote Shared Domestic Responsibilities", "Ensure Full Participation in Leadership and Decision-Making", "Universal Access to Reproductive Health and Rights", "Equal Rights to Economic Resources, Property Ownership and Financial Services", "Promote Empowerment of Women Through Technology", "Adopt and Strengthen Policies and Enforceable Legislation for Gender Equality"],
    6: ["Safe and Affordable Drinking Water", "End Open Defecation and Provide Access to Sanitation and Hygiene", "Improve Water Quality, Wastewater Treatment and Safe Reuse", "Increase Water-Use Efficiency and Ensure Freshwater Supplies", "Implement Integrated Water Resources Management", "Protect and Restore Water-Related Ecosystems", "Expand Water and Sanitation Support to Developing Countries", "Support Local Engagement in Water and Sanitation Management"],
    7: ["Universal Access to Modern Energy", "Increase Global Percentage of Renewable Energy", "Double the Improvement in Energy Efficiency", "Promote Access Research, Technology and Investments in Clean Energy", "Expand and Upgrade Energy Services for Developing Countries"],
    8: ["Sustainable Economic Growth", "Diversify, Innovate and Upgrade for Economic Productivity", "Promote Policies to Support Job Creation and Growing Enterprises", "Improve Resource Efficiency in Consumption and Production", "Full Employment and Decent Work with Equal Pay", "Promote Youth Employment, Education and Training", "End Modern Slavery, Trafficking and Child Labour", "Protect Labour Rights and Promote Safe and Secure Working Environments", "Promote Beneficial and Sustainable Tourism", "Universal Access to Banking, Insurance and Financial Services", "Increase Aid for Trade Support", "Develop a Global Youth Employment Strategy"],
    9: ["Develop Sustainable, Resilient and Inclusive Infrastructures", "Promote Inclusive and Sustainable Industrialization", "Increase Access to Financial Services and Markets", "Upgrade All Industries and Infrastructures for Sustainability", "Enhance Scientific Research and Upgrade Industrial Technologies", "Facilitate Sustainable Infrastructure Development for Developing Countries", "Support Domestic Technology Development and Industrial Diversification", "Universal Access to Information and Communications Technology"],
    10: ["Reduce Income Inequalities", "Promote Universal Social, Economic and Political Inclusion", "Ensure Equal Opportunities and End Discrimination", "Adopt Fiscal and Social Policies that Promotes Equality", "Improved Regulation of Global Financial Markets and Institutions", "Enhanced Representation for Developing Countries in Financial Institutions", "Responsible and Well-Managed Migration Policies", "Special and Differential Treatment for Developing Countries", "Encourage Development Assistance and Investment in Least Developed Countries", "Reduce Transaction Costs for Migrant Remittances"],
    11: ["Safe and Affordable Housing", "Affordable and Sustainable Transport Systems", "Inclusive and Sustainable Urbanization", "Protect the World's Cultural Heritage", "Reduce the Adverse Effects of Natural Disasters", "Reduce the Environmental Impact of Cities", "Provide Access to Safe and Inclusive Green and Public Spaces", "Strong National and Regional Development Planning", "Support Least Developed Countries in Sustainable and Resilient Building", "Reduce the Number of Deaths and People Affected by Disasters", "Reduce the Environmental Impact of Cities", "Provide Access to Safe and Inclusive Green and Public Spaces", "Reduce the Economic, Social and Environmental Impacts of Urbanization", "Strengthen National and Regional Development Planning", "Implement Policies for Inclusion, Resource Efficiency and Disaster Risk Reduction", "Support Least Developed Countries in Sustainable and Resilient Building"],
    12: ["Implement the 10-Year Sustainable Consumption and Production Framework", "Sustainable Management Use of Natural Resources", "Halve Global Per Capita Food Waste", "Responsible Management of Chemicals and Waste", "Substantially Reduce Waste Generation", "Encourage Companies to Adopt Sustainable Practices and Sustainability Reporting", "Promote Sustainable Public Procurement Practices", "Promote Universal Understanding of Sustainable Lifestyles", "Support Developing Countries' Scientific and Technological Capacity for Sustainable Consumption and Production", "Develop and Implement Tools to Monitor Sustainable Tourism", "Remove Market Distortions That Encourage Wasteful Consumption"],
    13: ["Strengthen Resilience and Adaptive Capacity to Climate Related Disasters", "Integrate Climate Change Measures into Policies and Planning", "Build Knowledge and Capacity to Meet Climate Change", "Implement the UN Framework Convention on Climate Change", "Promote Mechanisms to Raise Capacity for Planning and Management"],
    14: ["Reduce Marine Pollution", "Protect and Restore Ecosystems", "Reduce Ocean Acidification", "Sustainable Fishing", "Conserve Coastal and Marine Areas", "End Subsidies Contributing to Overfishing", "Increase the Economic Benefits from Sustainable Use of Marine Resources", "Increase Scientific Knowledge, Research and Technology for Ocean Health", "Support Small Scale Fishers", "Implement and Enforce International Sea Law"],
    15: ["Conserve and Restore Terrestrial and Freshwater Ecosystems", "End Deforestation and Restore Degraded Forests", "End Desertification and Restore Degraded Land", "Ensure Conservation of Mountain Ecosystems", "Protect Biodiversity and Natural Habitats", "Promote Access to Genetic Resources and Fair Sharing of the Benefits", "Eliminate Poaching and Trafficking of Protected Species", "Prevent Invasive Alien Species on Land and in Water Ecosystems", "Integrate Ecosystem and Biodiversity in Governmental Planning", "Increase Financial Resources to Conserve and Sustainably Use Ecosystems and Biodiversity", "Finance and Incentivize Sustainable Forest Management", "Combat Poaching and Trafficking"],
    16: ["Reduce Violence Everywhere", "Protect Children from Abuse, Exploitation, Trafficking and Violence", "Promote the Rule of Law and Ensure Equal Access to Justice", "Combat Organized Crime and Illicit Financial and Arms Flows", "Substantially Reduce Corruption and Bribery", "Develop Effective, Accountable and Transparent Institutions", "Ensure Responsive, Inclusive and Representative Decision-Making", "Strengthen the Participation in Global Governance", "Provide Universal Legal Identity", "Ensure Public Access to Information and Protect Fundamental Freedoms", "Strengthen National Institutions to Prevent Violence and Combat Terrorism and Crime", "Promote and Enforce Non-Discriminatory Laws and Policies"],
    17: ["Mobilize Resources to Improve Domestic Revenue Collection", "Implement All Development Assistance Commitments", "Mobilize Financial Resources For Developing Countries", "Assist Developing Countries in Attaining Debt Sustainability", "Invest in Least Developed Countries", "Knowledge Sharing and Cooperation for Access to Science, Technology and Innovation", "Promote Sustainable Technologies to Developing Countries", "Strengthen the Science, Technology and Innovation Capacity for Least Developed Countries", "Enhance SDG Capacity in Developing Countries", "Promote a Universal Trading System Under the WTO", "Increase the Exports of Developing Countries", "Remove Trade Barriers for Least Developed Countries", "Enhance Global Macroeconomic Stability", "Enhance Policy Coherence for Sustainable Development", "Respect National Leadership to Implement Policies for the Sustainable Development Goals", "Enhance the Global Partnership for Sustainable Development", "Encourage Effective Partnerships", "Enhance Availability of Reliable Data", "Further Develop Measurements of Progress"]
}


goals_collection.insert_many(goal_data)

# Construct target documents from indices and texts

target_counter = 0 # to have access to the
target_data = []
for goal_index, indices in target_indices.items():
    for i, index in enumerate(indices):

        target_svg_path_template = mongodb_sdg_settings.TARGET_SVG_PATH_TEMPLATE
        target_svg_path = target_svg_path_template.format(goal_index=goal_index, index=index)

        if os.path.exists(target_svg_path):
            encoded_svg = encode_svg_to_base64(target_svg_path)
        else:
            encoded_svg = None  # or handle missing SVG files as needed


        target = {
            "index": index,
            "text": target_texts[goal_index][i],
            "color": goal_data[goal_index - 1]['color'],
            "goalIndex": goal_index,
            "targetVectorIndex": target_counter,
            "icon": encoded_svg  # Adding encoded SVG for the target
        }
        target_data.append(target)
        target_counter+= 1
targets_collection.insert_many(target_data)


# Verify by fetching the documents
inserted_goals = list(goals_collection.find({}))
inserted_targets = list(targets_collection.find({}))

print("Inserted Goal Documents:")
for goal in inserted_goals:
    print(goal)

print("Inserted Target Documents:")
for target in inserted_targets:
    print(target)

client.close()
