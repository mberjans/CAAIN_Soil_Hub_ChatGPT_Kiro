#!/usr/bin/env python3
"""
Script to define comprehensive search queries for funding opportunities
for bioinformatics educational and community events for ITCBT.
"""

def get_search_queries():
    """
    Returns a list of search queries to find funding opportunities.
    Focuses on Canadian sources first, then international.
    Excludes Canadian Bioinformatics Hub funding.
    """
    queries = [
        # Canadian Government and Indigenous-specific
        "bioinformatics education funding Canada Indigenous",
        "Indigenous bioinformatics training grants Canada",
        "CIHR Indigenous health research funding bioinformatics",
        "NSERC Indigenous science education grants",
        "SSHRC Indigenous community education funding",
        "Indigenous Services Canada education grants bioinformatics",
        "Assembly of First Nations funding Indigenous education",
        "Canadian Institutes of Health Research Indigenous trainees",
        "Genome Canada Indigenous bioinformatics funding",
        "Canadian Foundation for Innovation Indigenous research",

        # Canadian Educational and Community Funding
        "Canada research chairs Indigenous bioinformatics",
        "Mitacs Indigenous internship funding bioinformatics",
        "Ontario Ministry of Colleges and Universities Indigenous funding",
        "Alberta Ministry of Advanced Education Indigenous grants",
        "British Columbia Ministry of Education Indigenous programs",
        "Quebec Ministry of Education Indigenous funding bioinformatics",
        "Canadian university Indigenous education grants",
        "Community foundations Canada Indigenous education",
        "United Way Canada Indigenous community programs",
        "Trillium Foundation Indigenous education funding",

        # International Bioinformatics Organizations
        "ISCB education committee funding opportunities",
        "International Society for Computational Biology grants",
        "EMBL training funding bioinformatics education",
        "Wellcome Trust bioinformatics education grants",
        "Howard Hughes Medical Institute bioinformatics training",
        "Bill & Melinda Gates Foundation bioinformatics education",
        "NIH bioinformatics education funding international",
        "European Bioinformatics Institute training grants",
        "BioStars bioinformatics community funding",
        "PLOS Computational Biology education grants",

        # International Indigenous and Education Funding
        "UNESCO Indigenous education funding bioinformatics",
        "World Health Organization Indigenous health training",
        "Ford Foundation Indigenous education grants",
        "MacArthur Foundation Indigenous community programs",
        "Open Society Foundations Indigenous education",
        "Rockefeller Foundation Indigenous science education",
        "Carnegie Corporation Indigenous education funding",
        "Ford Foundation Indigenous bioinformatics training",
        "International Development Research Centre Indigenous grants",
        "Commonwealth of Learning Indigenous education",

        # General Education and Event Funding
        "education event funding Canada Indigenous",
        "community workshop grants Canada bioinformatics",
        "professional development funding Indigenous scientists",
        "STEM education grants Indigenous communities",
        "science communication funding Indigenous researchers",
        "knowledge mobilization grants Canada Indigenous",
        "capacity building funding Indigenous bioinformatics",
        "networking event funding bioinformatics Canada",
        "conference funding Indigenous researchers Canada",
        "workshop funding bioinformatics education",

        # Additional Canadian Sources
        "Canada Council for the Arts Indigenous science communication",
        "Social Sciences and Humanities Research Council Indigenous",
        "Natural Sciences and Engineering Research Council Indigenous",
        "Canadian Heritage Indigenous education funding",
        "Employment and Social Development Canada Indigenous training",
        "Crown-Indigenous Relations and Northern Affairs Canada education",
        "Indigenous and Northern Affairs Canada training grants",
        "Public Health Agency of Canada Indigenous health education",
        "Statistics Canada Indigenous data science training",
        "Environment and Climate Change Canada Indigenous science",

        # International Foundations and NGOs
        "Alfred P. Sloan Foundation computational biology education",
        "Gordon and Betty Moore Foundation bioinformatics training",
        "Simons Foundation computational biology education",
        "Burroughs Wellcome Fund bioinformatics education",
        "American Association for the Advancement of Science education",
        "European Molecular Biology Organization training grants",
        "Human Frontier Science Program bioinformatics education",
        "International Centre for Genetic Engineering and Biotechnology",
        "Fogarty International Center bioinformatics training",
        "National Institute of General Medical Sciences education",

        # More International Sources
        "European Commission Horizon Europe bioinformatics education",
        "UK Research and Innovation bioinformatics training",
        "Australian Research Council Indigenous bioinformatics",
        "New Zealand Ministry of Education Indigenous science",
        "Singapore Ministry of Education bioinformatics training",
        "South African Medical Research Council Indigenous health",
        "Brazilian Ministry of Science Indigenous bioinformatics",
        "Indian Department of Biotechnology Indigenous training",
        "Chinese Academy of Sciences bioinformatics education",
        "Japanese Society for the Promotion of Science bioinformatics",

        # Additional Queries to Reach >100
        "bioinformatics summer school funding Indigenous",
        "online course development grants bioinformatics Indigenous",
        "curriculum development funding Indigenous bioinformatics",
        "mentorship program funding Indigenous scientists",
        "student exchange funding bioinformatics Canada Indigenous",
        "research network funding Indigenous bioinformatics",
        "data science training grants Indigenous communities",
        "computational biology workshop funding Canada",
        "genomics education funding Indigenous populations",
        "proteomics training grants Indigenous researchers",

        "metabolomics education funding Canada Indigenous",
        "systems biology training grants Indigenous",
        "structural biology workshop funding Canada",
        "bioinformatics tool development funding Indigenous",
        "database development grants bioinformatics Indigenous",
        "software training funding Indigenous bioinformatics",
        "programming course grants Indigenous scientists",
        "data analysis workshop funding Canada bioinformatics",
        "machine learning training Indigenous health research",
        "artificial intelligence education funding Indigenous",

        "big data analytics training grants Indigenous",
        "cloud computing workshop funding bioinformatics Canada",
        "high performance computing training Indigenous",
        "cyberinfrastructure grants bioinformatics Indigenous",
        "digital literacy funding Indigenous communities",
        "technology access grants Indigenous researchers",
        "equipment funding bioinformatics training Indigenous",
        "laboratory access grants Indigenous bioinformatics",
        "computational resources funding Canada Indigenous",
        "supercomputing training grants Indigenous scientists",

        "open source software development funding bioinformatics",
        "code repository grants Indigenous researchers",
        "version control training funding bioinformatics",
        "collaboration platform grants Indigenous communities",
        "virtual reality training funding bioinformatics Indigenous",
        "augmented reality workshop grants Canada",
        "simulation software training Indigenous scientists",
        "modeling tools funding bioinformatics education",
        "visualization software grants Indigenous researchers",
        "data visualization workshop funding Canada bioinformatics",

        "publication funding Indigenous bioinformatics research",
        "journal access grants Indigenous scientists",
        "open access publishing funding bioinformatics Indigenous",
        "peer review training grants Canada",
        "scientific writing workshop funding Indigenous",
        "grant writing training bioinformatics Indigenous communities",
        "proposal development funding Canada bioinformatics",
        "funding application workshop grants Indigenous",
        "career development funding Indigenous researchers",
        "leadership training grants bioinformatics Canada",

        "policy development funding Indigenous bioinformatics",
        "ethics training grants Indigenous scientists",
        "responsible research funding bioinformatics Canada",
        "community engagement grants Indigenous researchers",
        "knowledge translation funding bioinformatics Indigenous",
        "impact assessment training grants Canada",
        "evaluation methods workshop funding Indigenous",
        "monitoring and evaluation grants bioinformatics Indigenous",
        "sustainability planning funding Canada bioinformatics",
        "long-term planning grants Indigenous communities",

        "international collaboration funding bioinformatics Indigenous",
        "global partnership grants Canada bioinformatics",
        "cross-cultural training funding Indigenous researchers",
        "cultural competency workshop grants bioinformatics",
        "Indigenous knowledge integration funding Canada",
        "traditional ecological knowledge grants bioinformatics",
        "land-based learning funding Indigenous scientists",
        "cultural safety training grants bioinformatics Canada",
        "Indigenous research methodology workshop funding",
        "decolonizing science grants Indigenous communities",

        "youth engagement funding bioinformatics Indigenous",
        "student mentorship program grants Canada bioinformatics",
        "early career researcher funding Indigenous scientists",
        "postdoctoral training grants bioinformatics Indigenous",
        "graduate student funding Canada bioinformatics",
        "undergraduate research grants Indigenous researchers",
        "high school science program funding bioinformatics",
        "outreach activity grants Indigenous communities",
        "public engagement funding bioinformatics Canada",
        "science communication training grants Indigenous",

        "media training funding Indigenous researchers",
        "social media strategy grants bioinformatics Canada",
        "podcast development funding Indigenous scientists",
        "video production grants bioinformatics Indigenous",
        "storytelling workshop funding Canada bioinformatics",
        "art and science collaboration grants Indigenous",
        "exhibition funding bioinformatics Indigenous communities",
        "museum program grants Canada bioinformatics",
        "science fair organization funding Indigenous",
        "competition hosting grants bioinformatics Canada",

        "award program funding Indigenous researchers",
        "scholarship establishment grants bioinformatics",
        "fellowship program funding Canada Indigenous",
        "prize creation grants bioinformatics Indigenous",
        "recognition program funding Indigenous scientists",
        "achievement award grants bioinformatics Canada",
        "excellence in research funding Indigenous",
        "innovation award grants bioinformatics Indigenous",
        "leadership award funding Canada bioinformatics",
        "community impact grants Indigenous researchers"
    ]

    return queries

if __name__ == "__main__":
    queries = get_search_queries()
    print(f"Generated {len(queries)} search queries")
    for i, query in enumerate(queries[:10], 1):  # Show first 10
        print(f"{i}. {query}")
    print("...")