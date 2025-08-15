# **🏥 Healthcare Provider Data Guide for Advisors**

## **📊 What's in the Dataset**

### **Core Data: 82,608 Healthcare Providers**
- **Source**: National Provider Identifier (NPI) database
- **Geographic Coverage**: 10 states (MN, CA, OR, WA, TX, AZ, IL, MD, VA, FL)
- **Provider Types**: 
  - **HCBS** (Home & Community-Based Services): 62,456 providers
  - **ALF** (Assisted Living Facilities): 20,152 providers
- **Complete Geocoding**: Every provider has precise latitude/longitude coordinates

### **Key Data Fields**

| Field | Description | Example |
|-------|-------------|---------|
| `npi` | National Provider Identifier | 1023011079 |
| `org_or_person_name` | Provider name | "ADVANTAGE HOME HEALTH CARE, INC." |
| `address_full` | Complete address | "425 E. US RT. 6 SUITE F, Morris, IL 60450" |
| `lat/lon` | GPS coordinates | 41.3889466, -88.4137571 |
| `state/zip` | Location | IL, 60450 |
| `provider_type` | HCBS or ALF | HCBS |
| `medicare_enrolled` | Accepts Medicare | True/False |
| `medicaid_enrolled` | Accepts Medicaid | True/False |
| `enrollment_status` | Combined status | "Both Medicare & Medicaid" |
| `medicaid_density` | Medicaid providers in ZIP | 0-405 |
| `medicare_density` | Medicare providers in ZIP | 0-300+ |

---

## **🎯 Key Insights from the Data**

### **1. Strong Provider Network Foundation**
- **80.4% of providers** accept Medicaid (66,402 providers)
- **69.1% of providers** accept Medicare (57,103 providers)
- **47,045 providers** accept both programs
- **Strong geographic coverage** across all 10 states

### **2. Provider Type Patterns**
- **HCBS Providers**: 85.8% accept Medicaid (excellent coverage)
- **ALF Providers**: 58.7% accept Medicaid (coverage gap)
- **HCBS dominance**: 75.6% of all providers are HCBS

### **3. Geographic Distribution**
- **Highest Medicaid acceptance**: Oregon (84.1%), Washington (83.5%), California (83.2%)
- **Lowest Medicaid acceptance**: Illinois (78.9%), Maryland (80.2%)
- **Urban concentration**: Higher provider density in metropolitan areas

---

## **🚨 Medicaid Density Areas at Risk**

### **High-Density Areas (50+ providers)**
**Total**: 25,025 providers in high-density areas
**Total Medicaid density**: 2,586,406

### **Top 10 Highest Density ZIP Codes**
1. **ZIP 77036 (TX)**: 466 providers, 405 density, 86.9% accept Medicaid
2. **ZIP 91411 (CA)**: 296 providers, 251 density, 84.8% accept Medicaid
3. **ZIP 77407 (TX)**: 294 providers, 237 density, 80.6% accept Medicaid
4. **ZIP 33186 (FL)**: 293 providers, 235 density, 80.2% accept Medicaid
5. **ZIP 33330 (FL)**: 268 providers, 232 density, 86.6% accept Medicaid

### **Areas at Risk of Losing Coverage**

#### **High-Density Areas with Low Medicaid Acceptance**
- **ZIP 33165 (FL)**: 142 density, 67.0% Medicaid acceptance
- **ZIP 33175 (FL)**: 136 density, 69.7% Medicaid acceptance
- **ZIP 33177 (FL)**: 76 density, 67.3% Medicaid acceptance
- **ZIP 33010 (FL)**: 70 density, 64.2% Medicaid acceptance
- **ZIP 85254 (AZ)**: 56 density, 66.7% Medicaid acceptance

#### **ALF-Heavy Areas at Risk**
- **ZIP 77036 (TX)**: 405 density, 46.2% Medicaid acceptance
- **ZIP 91411 (CA)**: 251 density, 33.3% Medicaid acceptance
- **ZIP 77083 (TX)**: 206 density, 52.6% Medicaid acceptance
- **ZIP 91401 (CA)**: 179 density, 54.5% Medicaid acceptance
- **ZIP 75243 (TX)**: 154 density, 42.9% Medicaid acceptance

---

## **🔍 How to Use the Data**

### **1. Geographic Analysis**
```python
# Find providers in specific ZIP codes
zip_providers = df[df['zip'] == '60450']

# Find providers by state
state_providers = df[df['state'] == 'IL']

# Find high-density areas
high_density = df[df['medicaid_density'] >= 50]
```

### **2. Medicare/Medicaid Analysis**
```python
# Medicaid providers only
medicaid_providers = df[df['medicaid_enrolled'] == True]

# Providers accepting both programs
dual_providers = df[df['enrollment_status'] == 'Both Medicare & Medicaid']

# Coverage gaps
gap_providers = df[df['enrollment_status'] == 'Neither']
```

### **3. Risk Assessment**
```python
# Areas with high density but low Medicaid acceptance
risk_areas = df[
    (df['medicaid_density'] >= 50) & 
    (df['medicaid_enrolled'] == False)
]

# ALF-heavy areas at risk
alf_risk = df[
    (df['provider_type'] == 'ALF') & 
    (df['medicaid_density'] >= 30) & 
    (df['medicaid_enrolled'] == False)
]
```

---

## **🗺️ Visualization in Kepler**

### **Upload Instructions**
1. Go to [Kepler.gl](https://kepler.gl/)
2. Upload `data/enriched/kepler_medicare_medicaid_demo.csv`
3. Configure for Medicare/Medicaid analysis

### **Recommended Visualizations**

#### **1. Medicaid Density Mapping**
```
Layer Type: Point
Color By: medicaid_density (quantitative)
Size: Fixed or by provider_type
Filter: medicaid_enrolled = True
```

#### **2. Risk Area Identification**
```
Layer Type: Point
Color By: enrollment_status
Size By: medicaid_density
Filter: medicaid_density >= 50
```

#### **3. Provider Type Distribution**
```
Layer Type: Point
Color By: provider_type
Size By: medicaid_density
Filter: medicaid_enrolled = True
```

---

## **📈 Strategic Questions to Ask**

### **Market Analysis**
1. **Geographic Opportunities**: Which states have the strongest provider networks?
2. **Service Gaps**: What services are underserved in high-density markets?
3. **Competitive Landscape**: How do we compare to competitors in each market?
4. **Growth Potential**: Which markets offer the best expansion opportunities?

### **Risk Assessment**
1. **Coverage Gaps**: Which areas are most vulnerable to Medicaid policy changes?
2. **Provider Concentration**: Are we over-reliant on certain geographic areas?
3. **Service Mix**: Do we have adequate HCBS vs ALF provider balance?
4. **Network Adequacy**: Can our network handle increased demand?

### **Operational Planning**
1. **Provider Recruitment**: Where should we focus recruitment efforts?
2. **Service Development**: What new services can we offer?
3. **Quality Assurance**: How can we maintain quality across the network?
4. **Technology Integration**: What systems would enhance our network?

---

## **🎯 Key Business Insights**

### **1. Market Strengths**
- **Strong HCBS network**: 85.8% Medicaid acceptance
- **Geographic diversity**: Coverage across 10 states
- **Dual enrollment**: 47,045 providers accept both programs
- **High-density markets**: 25,025 providers in high-density areas

### **2. Market Opportunities**
- **ALF expansion**: Only 58.7% Medicaid acceptance
- **Geographic gaps**: Some states have lower acceptance rates
- **Service innovation**: Opportunity for new service models
- **Technology integration**: Digital solutions for network management

### **3. Risk Factors**
- **Policy changes**: Medicaid policy changes could impact coverage
- **Geographic concentration**: Some areas have very high provider density
- **Provider type imbalance**: ALF providers have lower Medicaid acceptance
- **Market competition**: High-density areas may have intense competition

---

## **💡 Strategic Recommendations**

### **Immediate Actions (0-6 months)**
1. **Risk Assessment**: Identify areas most vulnerable to Medicaid changes
2. **Provider Outreach**: Strengthen relationships with existing providers
3. **Geographic Analysis**: Map provider network adequacy by region
4. **Quality Assurance**: Implement provider quality metrics

### **Medium-term Initiatives (6-18 months)**
1. **Network Expansion**: Recruit providers in identified gap areas
2. **Service Innovation**: Develop new service models
3. **Technology Investment**: Implement network management systems
4. **Market Differentiation**: Develop unique value propositions

### **Long-term Strategy (18+ months)**
1. **Market Leadership**: Achieve dominant position in key markets
2. **Service Excellence**: Become the preferred provider network
3. **Technology Leadership**: Lead in digital health solutions
4. **Quality Standards**: Set industry standards for provider networks

---

## **📊 Success Metrics**

### **Network Adequacy Targets**
- **Medicaid Acceptance**: Maintain 80%+ acceptance rate
- **Geographic Coverage**: Ensure coverage in 95%+ of target areas
- **Provider Diversity**: Maintain balanced HCBS/ALF mix
- **Quality Scores**: Achieve 95%+ provider quality scores

### **Market Performance Goals**
- **Market Share**: Increase provider network participation
- **Service Expansion**: Launch new service lines
- **Geographic Growth**: Enter new markets
- **Provider Satisfaction**: Increase provider retention

This data provides a comprehensive foundation for strategic healthcare network planning and policy development, revealing both opportunities for growth and areas requiring attention.
