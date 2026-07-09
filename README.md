# Deutschlandticket Adoption Analysis - Project Overview

![Dashboard Screenshot](dashboard.png)

## Project Goal
Analyze whether introducing the Deutschlandticket could make commuting easier, cheaper, and more sustainable for J&J employees in the Hamburg metropolitan area.

## 🚀 Quick Setup

### One-Command Setup
Run the setup script to automatically create the environment and install all dependencies:

```bash
./setup.sh
```

### Manual Setup
If you prefer manual setup:

```bash
# Create conda environment
conda create -n jandj python=3.10 -y
conda activate jandj

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data
```

## 📊 Interactive Dashboard

The interactive Streamlit dashboard can be launched immediately after setup using the pre-generated data:

```bash
streamlit run streamlit_dashboard.py
```

The dashboard will be available at `http://localhost:8501`

**Note:** The dashboard uses pre-generated data files included in the repository, so you don't need to run the analysis notebooks first. Only run the notebooks if you want to regenerate the data from scratch.

### Dashboard Features:
- **🗺️ Interactive Map** - Employee locations, office, HVV stations with layer control
- **📊 Analytics** - Commute time and adoption score distributions
- **👥 Employee Explorer** - Searchable employee data table
- **🔄 Scenario Comparison** - Financial analysis across cost scenarios
- **🎛️ Real-time Filters** - Filter by commute time, adoption score, distance
- **📥 Export** - Download filtered data as CSV


## 📝 Project Structure
- **01_data_generation.ipynb** - Synthetic employee data generation (optional - run only if regenerating data)
- **02_geocoding.ipynb** - Address geocoding coordinates (optional - run only if regenerating data)
- **03_station_analysis.ipynb** - Multi-candidate station identification (optional - run only if regenerating data)
- **04_commute_routing.ipynb** - Public transport and car routing (optional - run only if regenerating data)
- **05_analysis_and_visualization.ipynb** - Adoption scoring and visualization (optional - run only if regenerating data)
- **streamlit_dashboard.py** - Interactive Streamlit dashboard (main interface)
- **setup.sh** - Automated setup script
- **requirements.txt** - Python dependencies

## Methodology & Decisions

### Multi-Candidate Station Approach
- **Approach:** Evaluate k=5 nearest stations per employee rather than using only the geographically nearest station

- **Decision Rationale:** The geographically nearest station may not provide the optimal commute time due to transit network structure, route connections, and service frequency

- **Implementation:** Calculate walking distances to 5 nearest stations, then evaluate all 25 combinations (5 employee stations × 5 office stations) to find minimal total commute time

- **Result:** 73.3% of employees benefit from multi-candidate approach over single-nearest-station approach

### Realistic Walking Distance Calculation
- **Approach:** Use LocationIQ API for walking distances instead of straight-line distance calculations

- **Decision Rationale:** Straight-line distance doesn't account for actual walking paths, roads, infrastructure, and barriers

- **Implementation:** Used LocationIQ API with caching to avoid redundant API calls and respect rate limits

- **Benefit:** More accurate walking time estimates for station accessibility assessment

### Car Routing for Real Comparison
- **Approach:** Use LocationIQ driving API with parking overhead for realistic car travel time comparison

- **Decision Rationale:** Car routing needs to include practical time costs (parking search, walking from parking) to compare fairly with public transport

- **Implementation:** Added 8-minute parking overhead to represent parking search time and walking from parking to office

- **Result:** Real car time comparison including practical considerations

### Adoption Scoring Framework
- **Approach:** Two-component framework (Transport Attractiveness 60% + Financial Attractiveness 40%)

- **Decision Rationale:** Separate transport (time/convenience) from financial (cost) factors to understand what drives adoption decisions

- **Transport Attractiveness:** Based on time ratio (PT time vs. car time) and walking penalty for accessibility

- **Financial Attractiveness:** Based on cost savings compared to driving costs

- **Weighting:** 60% transport, 40% financial - emphasizes practicality while acknowledging cost importance

### Cost Scenarios Analysis
- **Approach:** Evaluate three subsidy scenarios (Company Pays Full, 50% Subsidy, Employee Pays Full)

- **Decision Rationale:** Test how different financial arrangements affect adoption potential

- **Finding:** All scenarios showed identical adoption results because driving costs (€343/month average) are so much higher than Deutschlandticket (€63/month) that cost doesn't differentiate decisions

- **Implication:** Adoption decisions are driven by time and convenience rather than who pays for the ticket

### Geographic Connectivity Analysis
- **Approach:** Analyze public transport availability and quality by distance ranges from office

- **Decision Rationale:** Understand which geographic areas have strong vs. weak public transport connectivity

- **Finding:** Distance from office strongly affects PT availability - 0-20km has good coverage, 20km+ has limited options

- **Insight:** Public transport connectivity is not uniform - geographic location significantly affects adoption potential

- **Strong Connectivity Areas:** 51 employees (38.9%) have commute times <45 minutes, with average transport attractiveness of 75.7/100

- **Weak Connectivity Areas:** 63 employees (48.1%) have commute times >60 minutes, with average transport attractiveness of 48.9/100

- **No PT Available:** 47 employees (26.4%) have no viable public transport routes

- **Geographic Distribution:** Strong connectivity concentrated in 10-20km range (47 employees), weak connectivity concentrated in 30-50km range (58 employees)

## Technical Implementation

### APIs Used
- **OpenTripPlanner (OTP):** Public transport routing (local server)
- **LocationIQ:** Walking and car routing (API key required)
- **Geocoding:** LocationIQ address to coordinates

### Caching Strategy
- **Geocoding cache:** `data/geocoding_cache.csv` (avoid redundant address geocoding API calls)
- **Walking distances cache:** `data/candidate_walking_distances_cache.csv` (avoid redundant walking distance API calls)
- **OTP routing cache:** `data/routing_cache.csv` (avoid redundant transit route calculations)
- **Car routing cache:** `data/car_routing_cache.csv` (avoid redundant car route calculations)
- **Benefits:** Faster re-runs, API quota conservation, cost savings
- **Note:** Cache files are pre-generated and included in the repository for immediate use

### Key Formulas
**Optimal Commute Time:**
```
Total Commute = walk_home_to_station + transit_time + walk_station_to_office
```

**Adoption Score:**
```
Adoption Score = (Transport Attractiveness × 0.6) + (Financial Attractiveness × 0.4)
```

## Key Results

### Commute-Time Distribution
- 178 total employees (synthetic)
- 131 (73.6%) have valid public transport routes
- 47 (26.4%) have no viable public transport routes
- 38.9% have reasonable commutes (<45 minutes)
- 48.1% have long commutes (>60 minutes)

### Deutschlandticket Adoption Potential
- 59% have High/Medium adoption potential
- Adoption driven by time/convenience (transport attractiveness: 62.2/100)
- Financial attractiveness is near-perfect (99.7/100) due to massive cost savings
- Cost advantage exists regardless of subsidy level

### Geographic Connectivity
- Strong connectivity areas: 51 employees (38.9%) with commute times <45 minutes
- Weak connectivity areas: 63 employees (48.1%) with commute times >60 minutes
- No PT available: 47 employees (26.4%) have no viable public transport routes
- Strong connectivity areas have average transport attractiveness of 75.7/100
- Weak connectivity areas have average transport attractiveness of 48.9/100
- Geographic distribution: Strong connectivity concentrated in 10-20km range, weak connectivity in 30-50km range

### Cost Scenario Analysis
**Finding:** All three cost scenarios (Company Pays Full, 50% Subsidy, Employee Pays Full) showed identical adoption results

**Reason:** Average driving cost is €343/month vs. Deutschlandticket cost of €63/month. This means employees save approximately €280/month regardless of who pays. The cost advantage is so large that whether the company pays or the employee pays doesn't change the financial attractiveness of the Deutschlandticket.

**Implication:** Adoption decisions are driven by time and convenience (practicality), not by who pays for the ticket. Even when employees pay the full €63/month, the cost savings over driving are so substantial that cost doesn't differentiate between scenarios.

### Strategic Recommendations
1. **Targeted Promotion:** Focus Deutschlandticket promotion on the 10-20km range where strong connectivity is concentrated (47 employees)
2. **Geographic Targeting:** Prioritize areas with high transport attractiveness scores (75.7/100 average in strong connectivity areas)
3. **Support Programs:** Consider additional support for employees in weak connectivity areas (30-50km range) with long commutes
4. **Alternative Solutions:** Develop alternatives for 26% of employees without viable public transport routes (car pooling, shuttle services)
5. **Data Validation:** Replace synthetic data with actual employee locations for accurate business decisions

## Limitations

### Data Limitations
- Synthetic employee data (not real employee locations)
- Geographic distribution may not reflect actual employee distribution
- Maximum commute distance: 64.2km (may be unrealistic for daily commuting)
- Driving cost estimate: €0.30/km (may not reflect actual German costs)
- Parking cost: €50/month (assumes paid parking, may not apply if company provides free parking)

### Methodology Limitations
- Single time point analysis (08:00 only) - represents morning commute snapshot
- No evening commute analysis or rush hour variations
- Cost advantage so large that subsidy scenarios don't differentiate adoption
- Hamburg-specific analysis (may not generalize to other locations)
- No employee preference data included

## Files Generated

### Data Files
- `synthetic_employees_geocoded.csv` - Employee coordinates
- `data/employee_candidate_stations_with_walking.csv` - Multi-candidate station data
- `data/jj_office_candidate_stations_with_walking.csv` - Office station candidates
- `data/hvv_stations_filtered.csv` - HVV station data
- `data/synthetic_employees_with_optimal_commutes.csv` - Final routing results with adoption scores
- `data/routing_cache.csv` - OTP transit route cache
- `data/car_routing_cache.csv` - Car routing cache

### Dashboard Files
- `streamlit_dashboard.py` - Interactive Streamlit dashboard

### Visualization Files
- `data/commute_time_distribution.png` - Commute time buckets
- `data/correlation_heatmap.png` - Component correlations
- `data/station_rank_selection.png` - Optimal station rank distribution
- `data/component_scores.png` - Average component scores
- `data/adoption_distribution.png` - Adoption category distribution
- `data/distance_distribution_and_pt_availability.png` - Geographic distribution
- `data/connectivity_quality_by_distance.png` - Connectivity quality by distance
- `data/strong_weak_connectivity_overview.png` - Strong vs weak connectivity overview

## Tools & Technologies

- **Python 3.10** - Main programming language
- **Jupyter Notebooks** - Analysis environment
- **Pandas** - Data manipulation
- **Matplotlib/Seaborn** - Visualizations
- **OpenTripPlanner** - Public transport routing
- **LocationIQ** - Walking and car routing
- **Folium** - Interactive mapping
- **Scikit-learn** - Geographic distance calculations

## Conclusion

This analysis demonstrates a comprehensive methodology for evaluating Deutschlandticket adoption potential. The multi-candidate station approach and realistic routing provide a solid foundation for understanding commuting patterns.

The key insight is that the Deutschlandticket's massive cost advantage over driving (€280/month savings) means that adoption decisions are driven primarily by time and convenience rather than cost. Whether the company pays or the employee pays doesn't significantly affect the financial attractiveness because the ticket is so much cheaper than driving regardless.

This suggests that for actual business decisions, the focus should be on improving the practical aspects of public transport (time, convenience, reliability) rather than just cost considerations.
