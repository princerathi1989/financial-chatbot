"""Financial document collector for permanent knowledge base."""

import os
import uuid
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

class FinancialDocumentCollector:
    """Collects financial documents from authoritative sources."""
    
    def __init__(self):
        self.base_dir = Path("storage/permanent_knowledge")
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_sample_documents(self) -> List[Dict[str, Any]]:
        """Collect sample financial documents for initial knowledge base."""
        documents = []
        
        # Sample financial knowledge documents
        sample_docs = [
            {
                'domain': 'stock_market',
                'title': 'Stock Market Basics',
                'content': self._get_stock_market_basics(),
                'filename': 'stock_market_basics.txt',
                'source': 'curated'
            },
            {
                'domain': 'mutual_funds',
                'title': 'Mutual Fund Investment Guide',
                'content': self._get_mutual_fund_guide(),
                'filename': 'mutual_fund_guide.txt',
                'source': 'curated'
            },
            {
                'domain': 'banking',
                'title': 'Banking Products Overview',
                'content': self._get_banking_products(),
                'filename': 'banking_products.txt',
                'source': 'curated'
            },
            {
                'domain': 'taxation',
                'title': 'Tax Planning Strategies',
                'content': self._get_tax_planning(),
                'filename': 'tax_planning.txt',
                'source': 'curated'
            },
            {
                'domain': 'insurance',
                'title': 'Insurance Products Guide',
                'content': self._get_insurance_guide(),
                'filename': 'insurance_guide.txt',
                'source': 'curated'
            },
            {
                'domain': 'real_estate',
                'title': 'Real Estate Investment Guide',
                'content': self._get_real_estate_guide(),
                'filename': 'real_estate_guide.txt',
                'source': 'curated'
            },
            {
                'domain': 'retirement',
                'title': 'Retirement Planning Guide',
                'content': self._get_retirement_planning(),
                'filename': 'retirement_planning.txt',
                'source': 'curated'
            },
            {
                'domain': 'gold_investment',
                'title': 'Gold Investment Guide',
                'content': self._get_gold_investment(),
                'filename': 'gold_investment.txt',
                'source': 'curated'
            }
        ]
        
        return sample_docs
    
    def _get_stock_market_basics(self) -> str:
        """Get stock market basics content."""
        return """
        STOCK MARKET BASICS
        
        1. What is a Stock Market?
        A stock market is a marketplace where shares of publicly traded companies are bought and sold. In India, the two major stock exchanges are the National Stock Exchange (NSE) and the Bombay Stock Exchange (BSE).
        
        2. Key Stock Market Indices
        - Nifty 50: Top 50 companies listed on NSE
        - Sensex: Top 30 companies listed on BSE
        - Bank Nifty: Banking sector stocks
        - Nifty IT: Information technology sector stocks
        
        3. Types of Stocks
        - Large Cap: Companies with market cap > ₹20,000 crores
        - Mid Cap: Companies with market cap ₹5,000-20,000 crores
        - Small Cap: Companies with market cap < ₹5,000 crores
        
        4. Investment Strategies
        - Value Investing: Buying undervalued stocks
        - Growth Investing: Investing in companies with high growth potential
        - Dividend Investing: Focusing on dividend-paying stocks
        - Index Investing: Investing in index funds or ETFs
        
        5. Risk Management
        - Diversification: Don't put all money in one stock
        - Stop Loss: Set predetermined exit points
        - Position Sizing: Don't risk more than 2-5% per trade
        - Research: Always research before investing
        
        6. Trading vs Investing
        - Trading: Short-term buying and selling (days/weeks)
        - Investing: Long-term holding (months/years)
        - Day Trading: Buying and selling within the same day
        
        7. Important Terms
        - P/E Ratio: Price-to-Earnings ratio
        - Market Cap: Total value of company's shares
        - Volume: Number of shares traded
        - Bid/Ask: Buy and sell prices
        - Circuit Breaker: Trading halt mechanism
        """
    
    def _get_mutual_fund_guide(self) -> str:
        """Get mutual fund investment guide content."""
        return """
        MUTUAL FUND INVESTMENT GUIDE
        
        1. What are Mutual Funds?
        Mutual funds pool money from multiple investors to invest in a diversified portfolio of stocks, bonds, or other securities managed by professional fund managers.
        
        2. Types of Mutual Funds
        
        A. By Asset Class:
        - Equity Funds: Invest primarily in stocks
        - Debt Funds: Invest in fixed-income securities
        - Hybrid Funds: Mix of equity and debt
        - Money Market Funds: Short-term debt instruments
        
        B. By Market Cap:
        - Large Cap Funds: Invest in large companies
        - Mid Cap Funds: Invest in mid-sized companies
        - Small Cap Funds: Invest in small companies
        - Multi Cap Funds: Invest across all market caps
        
        C. By Investment Style:
        - Index Funds: Track market indices
        - Active Funds: Managed by fund managers
        - Sectoral Funds: Focus on specific sectors
        - Thematic Funds: Focus on specific themes
        
        3. Key Metrics to Consider
        - NAV (Net Asset Value): Price per unit
        - Expense Ratio: Annual fees charged
        - Alpha: Excess returns over benchmark
        - Beta: Volatility relative to market
        - Sharpe Ratio: Risk-adjusted returns
        - Standard Deviation: Volatility measure
        
        4. Investment Strategies
        - SIP (Systematic Investment Plan): Regular monthly investments
        - Lump Sum: One-time large investment
        - STP (Systematic Transfer Plan): Transfer between funds
        - SWP (Systematic Withdrawal Plan): Regular withdrawals
        
        5. Tax Benefits
        - ELSS (Equity Linked Savings Scheme): Tax deduction under 80C
        - Long-term capital gains tax: 10% on gains > ₹1 lakh
        - Short-term capital gains tax: 15% on equity funds
        
        6. Risk Factors
        - Market Risk: Fluctuations in market prices
        - Credit Risk: Default by issuers
        - Liquidity Risk: Difficulty in selling
        - Interest Rate Risk: Impact of rate changes
        
        7. Selection Criteria
        - Fund Performance: Historical returns
        - Fund Manager Track Record: Experience and performance
        - Fund House Reputation: AMC credibility
        - Expense Ratio: Lower is better
        - AUM (Assets Under Management): Size of fund
        """
    
    def _get_banking_products(self) -> str:
        """Get banking products overview content."""
        return """
        BANKING PRODUCTS OVERVIEW
        
        1. Deposit Products
        
        A. Fixed Deposits (FD)
        - Interest rates: 5-7% p.a.
        - Tenure: 7 days to 10 years
        - Premature withdrawal: Penalty applies
        - Tax: TDS on interest > ₹40,000 p.a.
        - Senior citizen benefits: 0.25-0.5% extra interest
        
        B. Recurring Deposits (RD)
        - Monthly investment: ₹500 minimum
        - Tenure: 6 months to 10 years
        - Interest: Compounded quarterly
        - Premature closure: Penalty applies
        
        C. Savings Account
        - Interest: 2.5-4% p.a.
        - Minimum balance: ₹500-₹10,000
        - ATM withdrawals: Free up to limit
        - Online banking: Usually free
        
        2. Loan Products
        
        A. Personal Loans
        - Interest rate: 10-24% p.a.
        - Amount: ₹50,000 to ₹50 lakhs
        - Tenure: 1-5 years
        - Processing fee: 1-3% of loan amount
        - Eligibility: Income, credit score, employment
        
        B. Home Loans
        - Interest rate: 8-12% p.a.
        - Amount: Up to ₹10 crores
        - Tenure: 5-30 years
        - Down payment: 10-20%
        - Tax benefits: Interest deduction under 24B
        
        C. Car Loans
        - Interest rate: 8-15% p.a.
        - Amount: Up to ₹1 crore
        - Tenure: 1-7 years
        - Down payment: 10-20%
        - Processing fee: ₹1,000-₹5,000
        
        3. Credit Cards
        - Annual fee: ₹500-₹5,000
        - Interest rate: 24-48% p.a.
        - Credit limit: ₹10,000 to ₹10 lakhs
        - Rewards: Cashback, points, miles
        - Benefits: Insurance, discounts, offers
        
        4. Investment Products
        - Mutual Funds: Through bank partnerships
        - Insurance: Life and general insurance
        - Demat Account: For stock trading
        - PPF: Public Provident Fund
        - NSC: National Savings Certificate
        """
    
    def _get_tax_planning(self) -> str:
        """Get tax planning strategies content."""
        return """
        TAX PLANNING STRATEGIES
        
        1. Income Tax Slabs (FY 2023-24)
        
        For Individuals < 60 years:
        - Up to ₹2.5 lakhs: Nil
        - ₹2.5-5 lakhs: 5%
        - ₹5-10 lakhs: 20%
        - Above ₹10 lakhs: 30%
        
        For Senior Citizens (60-80 years):
        - Up to ₹3 lakhs: Nil
        - ₹3-5 lakhs: 5%
        - ₹5-10 lakhs: 20%
        - Above ₹10 lakhs: 30%
        
        2. Tax Saving Investments (Section 80C)
        - ELSS Mutual Funds: ₹1.5 lakhs
        - PPF: ₹1.5 lakhs
        - EPF: ₹1.5 lakhs
        - NSC: ₹1.5 lakhs
        - Tax-saving FDs: ₹1.5 lakhs
        - Life Insurance Premium: ₹1.5 lakhs
        
        3. Other Tax Deductions
        - Section 80D: Health Insurance Premium (₹25,000-₹1 lakh)
        - Section 80E: Education Loan Interest (No limit)
        - Section 80G: Donations (50-100% deduction)
        - Section 24B: Home Loan Interest (₹2 lakhs)
        - Section 80EE: First-time Home Buyer (₹50,000)
        
        4. Capital Gains Tax
        
        A. Long-term Capital Gains (LTCG)
        - Equity: 10% on gains > ₹1 lakh
        - Debt: 20% with indexation
        - Real Estate: 20% with indexation
        
        B. Short-term Capital Gains (STCG)
        - Equity: 15%
        - Debt: As per income tax slab
        - Real Estate: As per income tax slab
        
        5. Tax Planning Strategies
        - Start Early: Begin tax planning at year start
        - Diversify: Use multiple tax-saving instruments
        - SIP in ELSS: Systematic investment for tax saving
        - Health Insurance: Cover family members
        - Home Loan: Maximize interest deduction
        - Donations: Plan charitable giving
        
        6. Important Deadlines
        - March 31: Last date for tax-saving investments
        - July 31: Income tax return filing deadline
        - December 31: Advance tax payment deadline
        
        7. Documents Required
        - Form 16: Salary certificate
        - Bank statements: Interest certificates
        - Investment proofs: Mutual fund statements
        - Insurance policies: Premium receipts
        - Home loan certificate: Interest statement
        """
    
    def _get_insurance_guide(self) -> str:
        """Get insurance products guide content."""
        return """
        INSURANCE PRODUCTS GUIDE
        
        1. Life Insurance
        
        A. Term Insurance
        - Pure protection: No investment component
        - Premium: ₹500-₹5,000 per month
        - Coverage: ₹50 lakhs to ₹5 crores
        - Tenure: 10-40 years
        - Tax benefit: Premium deduction under 80C
        
        B. Whole Life Insurance
        - Coverage: Entire lifetime
        - Premium: Higher than term insurance
        - Benefits: Death benefit + cash value
        - Surrender: Can surrender for cash value
        
        C. Endowment Plans
        - Savings + Protection: Investment component
        - Maturity benefit: Guaranteed returns
        - Premium: ₹1,000-₹10,000 per month
        - Tenure: 10-25 years
        
        D. ULIP (Unit Linked Insurance Plans)
        - Investment + Protection: Market-linked
        - Premium: ₹1,000-₹50,000 per month
        - Fund options: Equity, debt, balanced
        - Flexibility: Switch between funds
        
        2. Health Insurance
        
        A. Individual Health Insurance
        - Coverage: ₹1-50 lakhs
        - Premium: ₹2,000-₹20,000 per year
        - Waiting period: 2-4 years for pre-existing diseases
        - Co-payment: 10-20% of claim amount
        
        B. Family Floater
        - Coverage: Entire family
        - Premium: ₹5,000-₹50,000 per year
        - Sum insured: Shared among family members
        - Benefits: Maternity, newborn coverage
        
        C. Senior Citizen Health Insurance
        - Age: 60+ years
        - Coverage: ₹1-25 lakhs
        - Premium: ₹10,000-₹50,000 per year
        - Benefits: Pre-existing disease coverage
        
        3. General Insurance
        
        A. Motor Insurance
        - Third-party: Mandatory by law
        - Comprehensive: Own damage + third-party
        - Premium: ₹2,000-₹20,000 per year
        - Benefits: Accident, theft, natural calamities
        
        B. Home Insurance
        - Coverage: Structure + contents
        - Premium: ₹1,000-₹10,000 per year
        - Benefits: Fire, theft, natural disasters
        - Sum insured: Based on property value
        
        C. Travel Insurance
        - Coverage: Medical, trip cancellation
        - Premium: ₹500-₹5,000 per trip
        - Benefits: Emergency medical, baggage loss
        - Validity: Trip duration
        
        4. Key Factors to Consider
        - Coverage amount: Adequate for needs
        - Premium affordability: Within budget
        - Claim settlement ratio: Company track record
        - Network hospitals: Cashless treatment
        - Waiting periods: Pre-existing conditions
        - Exclusions: What's not covered
        
        5. Tax Benefits
        - Life Insurance Premium: Deduction under 80C
        - Health Insurance Premium: Deduction under 80D
        - Medical expenses: Deduction under 80DDB
        - Disability insurance: Deduction under 80U
        
        6. Claim Process
        - Intimate claim: Within 30 days
        - Submit documents: Medical reports, bills
        - Survey: For high-value claims
        - Settlement: Within 30 days of approval
        - Cashless: Direct settlement with hospital
        """
    
    def _get_real_estate_guide(self) -> str:
        """Get real estate investment guide content."""
        return """
        REAL ESTATE INVESTMENT GUIDE
        
        1. Types of Real Estate Investment
        
        A. Residential Real Estate
        - Apartments: Individual units in multi-story buildings
        - Villas: Independent houses with land
        - Plots: Empty land for construction
        - Builder floors: Independent floors in buildings
        
        B. Commercial Real Estate
        - Office spaces: Corporate offices and co-working spaces
        - Retail spaces: Shops, malls, and showrooms
        - Warehouses: Storage and logistics facilities
        - Hotels: Hospitality properties
        
        C. REITs (Real Estate Investment Trusts)
        - Listed REITs: Trade on stock exchanges
        - Private REITs: Non-listed investment trusts
        - Infrastructure REITs: Focus on infrastructure assets
        
        2. Investment Strategies
        
        A. Buy and Hold
        - Long-term rental income
        - Capital appreciation over time
        - Tax benefits on rental income
        - Property value appreciation
        
        B. Fix and Flip
        - Buy undervalued properties
        - Renovate and improve
        - Sell for profit
        - Short-term investment strategy
        
        C. Rental Income
        - Monthly rental income
        - Property appreciation
        - Tax deductions on expenses
        - Passive income generation
        
        3. Financial Analysis
        
        A. Rental Yield Calculation
        - Annual rental income / Property value × 100
        - Good yield: 6-8% in metro cities
        - Higher yield: 8-12% in tier-2 cities
        
        B. Capital Appreciation
        - Historical price trends
        - Location development potential
        - Infrastructure projects impact
        - Market demand-supply dynamics
        
        C. Cash Flow Analysis
        - Monthly rental income
        - Monthly expenses (EMI, maintenance, taxes)
        - Net cash flow calculation
        - Break-even analysis
        
        4. Financing Options
        
        A. Home Loans
        - Interest rates: 8-12% p.a.
        - Loan-to-value: 80-90%
        - Tenure: 5-30 years
        - Tax benefits: Interest deduction under 24B
        
        B. Construction Loans
        - For under-construction properties
        - Disbursed in stages
        - Higher interest rates
        - Converted to home loan post-completion
        
        C. Investment Property Loans
        - Higher interest rates than home loans
        - Lower loan-to-value ratio
        - Stricter eligibility criteria
        - Higher down payment requirements
        
        5. Legal Considerations
        
        A. Property Documents
        - Sale deed: Ownership transfer document
        - Title deed: Proof of ownership
        - Encumbrance certificate: No legal dues
        - Building approval: Construction permission
        
        B. Due Diligence
        - Title verification
        - Legal opinion from lawyer
        - Property inspection
        - Market valuation
        
        C. Registration and Stamp Duty
        - Registration charges: 1% of property value
        - Stamp duty: 5-7% of property value
        - Mutation: Update in revenue records
        - Property tax: Annual municipal tax
        
        6. Tax Implications
        
        A. Rental Income Tax
        - Taxable as income from house property
        - Standard deduction: 30% of rental income
        - Interest on home loan: Deductible
        - Property tax: Deductible expense
        
        B. Capital Gains Tax
        - Long-term: 20% with indexation (holding > 2 years)
        - Short-term: As per income tax slab
        - Exemption: Reinvestment in another property
        - TDS: 1% on sale consideration > ₹50 lakhs
        
        7. Risk Factors
        
        A. Market Risk
        - Property price fluctuations
        - Economic downturns impact
        - Interest rate changes
        - Liquidity constraints
        
        B. Legal Risk
        - Title disputes
        - Construction delays
        - Regulatory changes
        - Litigation issues
        
        C. Operational Risk
        - Maintenance costs
        - Vacancy periods
        - Tenant issues
        - Property damage
        """
    
    def _get_retirement_planning(self) -> str:
        """Get retirement planning guide content."""
        return """
        RETIREMENT PLANNING GUIDE
        
        1. Retirement Planning Basics
        
        A. Why Plan for Retirement?
        - Rising life expectancy (75+ years)
        - Inflation impact on purchasing power
        - Healthcare costs increase with age
        - Loss of regular income post-retirement
        - Social security may not be sufficient
        
        B. Retirement Corpus Calculation
        - Current annual expenses × 25-30 years
        - Consider inflation rate (6-7% p.a.)
        - Factor in healthcare costs
        - Include emergency fund
        - Account for lifestyle changes
        
        C. Retirement Age Considerations
        - Government employees: 60 years
        - Private sector: 58-65 years
        - Early retirement: 50-55 years
        - Late retirement: 65+ years
        
        2. Retirement Investment Vehicles
        
        A. Employee Provident Fund (EPF)
        - Mandatory for salaried employees
        - Interest rate: 8-9% p.a.
        - Tax-free withdrawal after 5 years
        - Employer contribution: 12% of basic salary
        - Employee contribution: 12% of basic salary
        
        B. National Pension System (NPS)
        - Voluntary retirement savings scheme
        - Tax deduction: ₹1.5 lakhs under 80C
        - Additional deduction: ₹50,000 under 80CCD(1B)
        - Partial withdrawal: 25% after 3 years
        - Annuity: 40% at maturity
        
        C. Public Provident Fund (PPF)
        - 15-year tenure with extensions
        - Interest rate: 7-8% p.a.
        - Tax deduction: ₹1.5 lakhs under 80C
        - Tax-free maturity
        - Minimum investment: ₹500 p.a.
        
        D. Atal Pension Yojana (APY)
        - For unorganized sector workers
        - Pension: ₹1,000-₹5,000 per month
        - Government co-contribution
        - Age: 18-40 years
        - Minimum contribution: ₹42-₹1,454 per month
        
        3. Retirement Investment Strategy
        
        A. Asset Allocation by Age
        - 20-30 years: 80% equity, 20% debt
        - 30-40 years: 70% equity, 30% debt
        - 40-50 years: 60% equity, 40% debt
        - 50-60 years: 40% equity, 60% debt
        - 60+ years: 20% equity, 80% debt
        
        B. Investment Options
        - Equity Mutual Funds: Long-term growth
        - Debt Mutual Funds: Stable returns
        - Hybrid Funds: Balanced approach
        - Index Funds: Low-cost equity exposure
        - Gold: Inflation hedge
        
        C. Systematic Investment Plan (SIP)
        - Regular monthly investments
        - Rupee cost averaging
        - Disciplined approach
        - Power of compounding
        - Flexible amounts
        
        4. Retirement Income Sources
        
        A. Pension Plans
        - Immediate annuity: Start immediately
        - Deferred annuity: Start later
        - Life annuity: Till death
        - Joint life annuity: For couples
        - Annuity with return of purchase price
        
        B. Systematic Withdrawal Plan (SWP)
        - Regular monthly withdrawals
        - From mutual fund investments
        - Tax-efficient withdrawals
        - Flexible withdrawal amounts
        - Maintains principal balance
        
        C. Rental Income
        - Property rental income
        - REIT dividends
        - Commercial property income
        - Residential rental income
        - Property appreciation
        
        5. Tax Planning for Retirement
        
        A. Tax-Free Investments
        - PPF: Tax-free maturity
        - EPF: Tax-free after 5 years
        - ELSS: Tax-free after 3 years
        - NPS: Partial tax-free withdrawal
        
        B. Tax-Efficient Withdrawals
        - Long-term capital gains: Lower tax rate
        - Indexation benefits: Reduce tax liability
        - Tax-loss harvesting: Offset gains
        - Systematic withdrawals: Spread tax burden
        
        C. Senior Citizen Benefits
        - Higher tax exemption limit
        - Deduction for medical expenses
        - Higher TDS threshold
        - Special savings schemes
        
        6. Healthcare Planning
        
        A. Health Insurance
        - Senior citizen health insurance
        - Family floater plans
        - Critical illness coverage
        - Pre-existing disease coverage
        - Cashless treatment facilities
        
        B. Medical Emergency Fund
        - 6-12 months of expenses
        - Liquid investments
        - Easy access to funds
        - Separate from retirement corpus
        - Regular review and update
        
        C. Long-term Care
        - Assisted living facilities
        - Home healthcare services
        - Medical equipment costs
        - Caregiver expenses
        - Healthcare inflation
        
        7. Estate Planning
        
        A. Will Preparation
        - Legal will document
        - Asset distribution
        - Beneficiary nomination
        - Executor appointment
        - Regular updates
        
        B. Nomination
        - Bank account nomination
        - Mutual fund nomination
        - Insurance nomination
        - Property nomination
        - Demat account nomination
        
        C. Power of Attorney
        - Financial power of attorney
        - Healthcare power of attorney
        - Durable power of attorney
        - Limited power of attorney
        - Revocable power of attorney
        """
    
    def _get_gold_investment(self) -> str:
        """Get gold investment guide content."""
        return """
        GOLD INVESTMENT GUIDE
        
        1. Why Invest in Gold?
        
        A. Hedge Against Inflation
        - Gold maintains purchasing power
        - Protects against currency devaluation
        - Historical inflation hedge
        - Store of value over centuries
        - Global acceptance
        
        B. Portfolio Diversification
        - Low correlation with stocks
        - Reduces overall portfolio risk
        - Safe haven asset
        - Crisis protection
        - Liquidity in emergencies
        
        C. Cultural and Emotional Value
        - Traditional investment in India
        - Wedding and festival purchases
        - Emotional attachment
        - Status symbol
        - Gift giving
        
        2. Forms of Gold Investment
        
        A. Physical Gold
        - Gold jewelry: High making charges
        - Gold coins: Low making charges
        - Gold bars: Lowest making charges
        - Storage and security concerns
        - Purity verification required
        
        B. Digital Gold
        - Gold ETFs: Exchange-traded funds
        - Gold mutual funds: Fund-based investment
        - Sovereign Gold Bonds (SGB): Government-backed
        - Gold savings schemes: Bank offerings
        - Gold futures: Derivative trading
        
        C. Gold Mining Stocks
        - Equity in gold mining companies
        - Higher volatility than physical gold
        - Dividend income potential
        - Management and operational risks
        - Leverage to gold prices
        
        3. Gold Investment Options
        
        A. Sovereign Gold Bonds (SGB)
        - Government-backed investment
        - Interest rate: 2.5% p.a.
        - Tenure: 8 years with exit options
        - Tax benefits: No capital gains tax
        - Minimum investment: 1 gram
        
        B. Gold ETFs
        - Exchange-traded funds
        - Low expense ratio: 0.5-1%
        - High liquidity
        - No storage concerns
        - Demat account required
        
        C. Gold Mutual Funds
        - Fund-based investment
        - Professional management
        - SIP options available
        - No demat account required
        - Higher expense ratio
        
        D. Gold Savings Schemes
        - Bank-offered schemes
        - Regular monthly investment
        - Physical gold delivery
        - Making charges applicable
        - Lock-in period varies
        
        4. Gold Price Determinants
        
        A. Global Factors
        - US dollar strength
        - Interest rates
        - Inflation expectations
        - Geopolitical tensions
        - Central bank policies
        
        B. Demand and Supply
        - Jewelry demand (50% of total)
        - Investment demand (40% of total)
        - Industrial demand (10% of total)
        - Mining production
        - Central bank purchases
        
        C. Economic Indicators
        - GDP growth rates
        - Inflation rates
        - Currency movements
        - Stock market performance
        - Bond yields
        
        5. Investment Strategies
        
        A. Systematic Investment
        - Regular monthly purchases
        - Rupee cost averaging
        - Reduces timing risk
        - Disciplined approach
        - Long-term wealth building
        
        B. Seasonal Investment
        - Festival season purchases
        - Wedding season demand
        - Price volatility patterns
        - Cultural buying patterns
        - Market timing
        
        C. Portfolio Allocation
        - 5-15% of total portfolio
        - Age-based allocation
        - Risk tolerance consideration
        - Rebalancing strategy
        - Regular review
        
        6. Tax Implications
        
        A. Physical Gold
        - Long-term capital gains: 20% with indexation
        - Short-term capital gains: As per income tax slab
        - Making charges: Not deductible
        - Storage costs: Not deductible
        - GST: 3% on purchase
        
        B. Digital Gold
        - Gold ETFs: Same as equity (STCG: 15%, LTCG: 10%)
        - Gold mutual funds: Same as debt funds
        - SGB: No capital gains tax
        - Gold futures: Speculation tax
        
        C. Tax Planning
        - Long-term holding: Lower tax rate
        - Indexation benefits: Reduce tax liability
        - Tax-loss harvesting: Offset gains
        - Systematic withdrawals: Spread tax burden
        
        7. Risk Factors
        
        A. Price Volatility
        - High short-term volatility
        - Currency fluctuation impact
        - Interest rate sensitivity
        - Market sentiment changes
        - Liquidity concerns
        
        B. Storage and Security
        - Theft and burglary risk
        - Insurance costs
        - Purity verification
        - Making charges
        - Resale value impact
        
        C. Market Risks
        - Regulatory changes
        - Technology disruption
        - Alternative investments
        - Economic downturns
        - Currency devaluation
        
        8. Best Practices
        
        A. Investment Timing
        - Avoid emotional buying
        - Focus on long-term trends
        - Dollar-cost averaging
        - Regular portfolio review
        - Rebalancing strategy
        
        B. Storage and Security
        - Bank lockers: Secure storage
        - Insurance coverage: Protect investment
        - Regular audits: Verify holdings
        - Documentation: Maintain records
        - Professional advice: Expert guidance
        
        C. Exit Strategy
        - Clear investment objectives
        - Regular portfolio review
        - Tax-efficient exits
        - Market timing consideration
        - Diversification maintenance
        """
    
    def save_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Save collected documents to permanent storage."""
        saved_paths = []
        
        for doc in documents:
            domain_dir = self.base_dir / doc['domain']
            domain_dir.mkdir(exist_ok=True)
            
            file_path = domain_dir / doc['filename']
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(doc['content'])
            
            saved_paths.append(str(file_path))
            logger.info(f"Saved {doc['title']} to {file_path}")
        
        return saved_paths

