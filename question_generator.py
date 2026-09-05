import json, os, random
from utils import topic_for_question

def load_seed_questions():
    try:
        from utils import load_questions
        questions = load_questions()
    except Exception:
        questions = []
    if len(questions) > 50:
        return questions
    return generate_seed_questions()

def generate_seed_questions():
    q = []
    topics = {
        'Alcohol': [
            {"q": "Which alcohol reacts fastest with Lucas reagent at room temperature?", "opts": ["Primary alcohol", "Secondary alcohol", "Tertiary alcohol", "Methanol"], "ans": "Tertiary alcohol", "type": "mc", "diff": 2},
            {"q": "What happens when ethanol is heated with concentrated H2SO4 at 170°C?", "opts": ["Forms ethane", "Forms ethene", "Forms ethanol oxide", "No reaction"], "ans": "Forms ethene", "type": "mc", "diff": 2},
            {"q": "The oxidation of primary alcohol first gives:", "opts": ["Aldehyde", "Ketone", "Carboxylic acid", "Ether"], "ans": "Aldehyde", "type": "mc", "diff": 1},
            {"q": "Which reagent is used to distinguish primary, secondary, and tertiary alcohols?", "opts": ["NaOH", "Lucas reagent", "AgNO3", "Br2 water"], "ans": "Lucas reagent", "type": "mc", "diff": 1},
            {"q": "T/F: Tertiary alcohols cannot be oxidized under normal conditions.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "Dehydration of 2-propanol gives mainly:", "opts": ["Propene", "2-Propyl ether", "Propanal", "2-Propanol stays"], "ans": "Propene", "type": "mc", "diff": 2},
            {"q": "Which alcohol is most acidic?", "opts": ["Methanol", "Ethanol", "Phenol", "tert-Butanol"], "ans": "Phenol", "type": "mc", "diff": 2},
            {"q": "The reaction of ethanol with sodium produces:", "opts": ["Ethanol sodium", "Sodium ethoxide + H2", "Ethyl sodium", "No reaction"], "ans": "Sodium ethoxide + H2", "type": "mc", "diff": 1},
            {"q": "Fill in the blank: The dehydration of alcohols follows _____ rule for Zaitsev product.", "opts": ["Zaitsev", "Markovnikov", "Hückel", "Saytzeff"], "ans": "Zaitsev", "type": "fib", "diff": 2},
            {"q": "T/F: Allylic and benzylic alcohols oxidize easily because the intermediate carbocation is resonance-stabilized.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "Which alcohol gives a positive iodoform test?", "opts": ["1-propanol", "2-butanol", "2-methyl-2-propanol", "2-propanol"], "ans": "2-propanol", "type": "mc", "diff": 2},
            {"q": "The Lucas test distinguishes alcohols based on:", "opts": ["Rate of formation of alkyl chloride", "Color change", "Gas evolution", "pH change"], "ans": "Rate of formation of alkyl chloride", "type": "mc", "diff": 2},
            {"q": "What product forms when ethylene glycol reacts with excess acetic anhydride?", "opts": ["Diacetate ester", "Ethanol", "Ethylene oxide", "Acetic acid"], "ans": "Diacetate ester", "type": "mc", "diff": 2},
            {"q": "Ethanol on oxidation with acidified K2Cr2O7 gives:", "opts": ["Ethanal then ethanoic acid", "Ethanol stays", "Ethyl acetate", "Ethane"], "ans": "Ethanal then ethanoic acid", "type": "mc", "diff": 1},
            {"q": "Which of the following is a secondary alcohol?", "opts": ["CH3CH2CH2OH", "CH3CH(OH)CH3", "(CH3)3COH", "CH3OH"], "ans": "CH3CH(OH)CH3", "type": "mc", "diff": 1},
        ],
        'Chemical Kinetics': [
            {"q": "The rate constant k doubles when temperature increases by 10°C. What is the approximate activation energy?", "opts": ["Low Ea", "High Ea", "Ea independent", "Ea = 0"], "ans": "Low Ea", "type": "mc", "diff": 3},
            {"q": "For a first-order reaction, the half-life is:", "opts": ["Dependent on initial concentration", "Independent of initial concentration", "Doubled when concentration doubles", "Zero"], "ans": "Independent of initial concentration", "type": "mc", "diff": 2},
            {"q": "The Arrhenius equation is:", "opts": ["k = Ae^(-Ea/RT)", "k = A + Ea/RT", "k = Ae^(Ea/RT)", "k = A/Ea"], "ans": "k = Ae^(-Ea/RT)", "type": "mc", "diff": 2},
            {"q": "A catalyst affects a reaction by:", "opts": ["Increasing Ea", "Lowering Ea", "Changing equilibrium", "Consumed in reaction"], "ans": "Lowering Ea", "type": "mc", "diff": 1},
            {"q": "T/F: The rate of a zero-order reaction is independent of reactant concentration.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "If the reaction rate doubles when [A] doubles, the reaction is _____ order in A.", "opts": ["First", "Second", "Zero", "Half"], "ans": "First", "type": "mc", "diff": 2},
            {"q": "The unit of rate constant for a second-order reaction is:", "opts": ["M/s", "M^-1 s^-1", "s^-1", "M^2 s^-1"], "ans": "M^-1 s^-1", "type": "mc", "diff": 2},
            {"q": "Which factor does NOT affect the rate of a chemical reaction?", "opts": ["Temperature", "Catalyst", "Pressure (for liquids)", "Concentration"], "ans": "Pressure (for liquids)", "type": "mc", "diff": 2},
            {"q": "T/F: The rate-determining step is the slowest step in a multi-step mechanism.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "The pre-exponential factor A in Arrhenius equation represents:", "opts": ["Frequency of collisions", "Activation energy", "Temperature", "Concentration"], "ans": "Frequency of collisions", "type": "mc", "diff": 3},
            {"q": "For a parallel reaction, the product distribution depends on:", "opts": ["Relative rates", "Temperature only", "Pressure only", "Catalyst only"], "ans": "Relative rates", "type": "mc", "diff": 3},
            {"q": "The collision theory states that molecules must:", "opts": ["Have sufficient energy and proper orientation", "Have same mass", "Be charged", "Be identical"], "ans": "Have sufficient energy and proper orientation", "type": "mc", "diff": 2},
            {"q": "The rate of a reaction increases with temperature because:", "opts": ["More molecules have energy ≥ Ea", "Concentration increases", "Volume decreases", "Catalyst forms"], "ans": "More molecules have energy ≥ Ea", "type": "mc", "diff": 2},
            {"q": "The half-life of a second-order reaction depends on:", "opts": ["Initial concentration", "Temperature only", "Catalyst only", "Volume"], "ans": "Initial concentration", "type": "mc", "diff": 3},
            {"q": "T/F: The rate law can be determined solely from the stoichiometric equation.", "opts": ["True", "False"], "ans": "False", "type": "tf", "diff": 2},
        ],
        'Electrochemistry': [
            {"q": "In a galvanic cell, oxidation occurs at the:", "opts": ["Anode", "Cathode", "Salt bridge", "Electrolyte"], "ans": "Anode", "type": "mc", "diff": 1},
            {"q": "The Nernst equation relates cell potential to:", "opts": ["Concentration", "Temperature", "Both A and B", "Neither"], "ans": "Both A and B", "type": "mc", "diff": 2},
            {"q": "Standard hydrogen electrode has a potential of:", "opts": ["0 V", "1 V", "-1 V", "0.5 V"], "ans": "0 V", "type": "mc", "diff": 1},
            {"q": "Faraday's first law states that the amount of substance deposited is proportional to:", "opts": ["Charge passed", "Time only", "Voltage only", "Current only"], "ans": "Charge passed", "type": "mc", "diff": 2},
            {"q": "T/F: In electrolysis, the anode is positive.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "The Gibbs free energy change for a spontaneous cell reaction is:", "opts": ["Negative", "Positive", "Zero", "Undefined"], "ans": "Negative", "type": "mc", "diff": 2},
            {"q": "A salt bridge in an electrochemical cell:", "opts": ["Maintains charge neutrality", "Provides electrons", "Stores current", "None"], "ans": "Maintains charge neutrality", "type": "mc", "diff": 2},
            {"q": "The standard cell potential E°cell is calculated as:", "opts": ["E°cathode - E°anode", "E°anode - E°cathode", "E°cathode + E°anode", "Neither"], "ans": "E°cathode - E°anode", "type": "mc", "diff": 2},
            {"q": "Which metal is most easily oxidized?", "opts": ["Li", "Cu", "Ag", "Au"], "ans": "Li", "type": "mc", "diff": 2},
            {"q": "During electrolysis of molten NaCl, products at anode and cathode are:", "opts": ["Cl2 at anode, Na at cathode", "Na at anode, Cl2 at cathode", "H2 and O2", "NaCl stays"], "ans": "Cl2 at anode, Na at cathode", "type": "mc", "diff": 2},
            {"q": "The cell potential decreases as reaction proceeds because:", "opts": ["Reactant concentrations change", "Temperature drops", "Electrodes dissolve", "Salt bridge breaks"], "ans": "Reactant concentrations change", "type": "mc", "diff": 3},
            {"q": "T/F: Corrosion of iron is an example of electrochemical cell.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "The EMF of a cell at equilibrium is:", "opts": ["Zero", "Maximum", "1 V", "Negative"], "ans": "Zero", "type": "mc", "diff": 2},
            {"q": "Fill in: The law that relates cell potential to Gibbs energy is ΔG = _____.", "opts": ["-nFE", "nFE", "-RTlnK", "Both A and C"], "ans": "-nFE", "type": "fib", "diff": 3},
            {"q": "Which is a reversible cell?", "opts": ["Daniel cell", "Lead-acid battery", "Fuel cell", "Both A and C"], "ans": "Daniel cell", "type": "mc", "diff": 3},
        ],
        'Ether': [
            {"q": "Diethyl ether is prepared by:", "opts": ["Dehydration of ethanol", "Reaction of ethanol with Na", "Williamson synthesis", "Both A and C"], "ans": "Both A and C", "type": "mc", "diff": 2},
            {"q": "What is the main product of ethanol with H2SO4 at 140°C?", "opts": ["Diethyl ether", "Ethene", "Ethanol oxide", "Ethyl hydrogen sulfate"], "ans": "Diethyl ether", "type": "mc", "diff": 2},
            {"q": "Ether cleavage with HI gives:", "opts": ["Alcohol and alkyl iodide", "Ketone", "Aldehyde", "No reaction"], "ans": "Alcohol and alkyl iodide", "type": "mc", "diff": 2},
            {"q": "T/F: Ethers are relatively unreactive due to the stability of the C–O bond.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "Epoxide ring opening with water in acid gives:", "opts": ["1,2-diol", "Ether", "Aldehyde", "Ketone"], "ans": "1,2-diol", "type": "mc", "diff": 2},
            {"q": "Which ether is commonly used as a solvent in Grignard reactions?", "opts": ["Diethyl ether", "Water", "Acetone", "Ethanol"], "ans": "Diethyl ether", "type": "mc", "diff": 1},
            {"q": "Peroxide formation in ethers occurs because:", "opts": ["Autoxidation", "Hydrolysis", "Dehydration", "Polymerization"], "ans": "Autoxidation", "type": "mc", "diff": 3},
            {"q": "T/F: THF is a cyclic ether used as a solvent.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "Which reagent cleaves an epoxide under basic conditions?", "opts": ["NaOH/H2O", "HCl", "H2SO4", "NaCl"], "ans": "NaOH/H2O", "type": "mc", "diff": 2},
            {"q": "The Williamson ether synthesis involves:", "opts": ["SN2 reaction", "SN1 reaction", "E1 elimination", "E2 elimination"], "ans": "SN2 reaction", "type": "mc", "diff": 2},
            {"q": "Fill in: Ethers on treatment with excess HI give _____ and alcohol.", "opts": ["Alkyl iodide", "Alkene", "Alkyne", "Aldehyde"], "ans": "Alkyl iodide", "type": "fib", "diff": 2},
            {"q": "T/F: Diethyl ether has a lower boiling point than ethanol due to inability to hydrogen bond as donor.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
        ],
        'Haloalkanes': [
            {"q": "Which halide undergoes SN2 fastest?", "opts": ["CH3Cl", "CH3CH2Cl", "(CH3)3CCl", "CH2=CHCl"], "ans": "CH3Cl", "type": "mc", "diff": 2},
            {"q": "SN2 reactions show:", "opts": ["Inversion of configuration", "Retention of configuration", "Racemization", "No stereochemistry"], "ans": "Inversion of configuration", "type": "mc", "diff": 2},
            {"q": "T/F: Tertiary alkyl halides prefer SN1 over SN2.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "Which halide undergoes E2 elimination fastest?", "opts": ["Primary", "Secondary", "Tertiary", "All equal"], "ans": "Tertiary", "type": "mc", "diff": 2},
            {"q": "Zaitsev's rule predicts the formation of:", "opts": ["More substituted alkene", "Less substituted alkene", "Terminal alkyne", "Cyclic alkene"], "ans": "More substituted alkene", "type": "mc", "diff": 2},
            {"q": "The rate of SN1 depends on:", "opts": ["Concentration of substrate only", "Concentration of nucleophile", "Both", "Neither"], "ans": "Concentration of substrate only", "type": "mc", "diff": 2},
            {"q": "T/F: Allylic halides undergo SN2 faster than primary halides.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "Which reagent can convert an alkyl halide to a Grignard reagent?", "opts": ["Mg in dry ether", "NaOH", "HCl", "KMnO4"], "ans": "Mg in dry ether", "type": "mc", "diff": 1},
            {"q": "Fill in: The conversion of an alkyl halide to an alkene using strong base is called _____ elimination.", "opts": ["E2", "SN2", "SN1", "E1"], "ans": "E2", "type": "fib", "diff": 2},
            {"q": "The order of reactivity for SN2 is:", "opts": ["CH3X > 1° > 2° > 3°", "3° > 2° > 1° > CH3X", "All equal", "1° > 2° > 3°"], "ans": "CH3X > 1° > 2° > 3°", "type": "mc", "diff": 2},
            {"q": "Which of the following has the highest boiling point?", "opts": ["1-chloropropane", "2-chloropropane", "1-chlorobutane", "2-chlorobutane"], "ans": "1-chlorobutane", "type": "mc", "diff": 3},
            {"q": "T/F: SN2 is favored by polar aprotic solvents.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "The product of chloroethane with KCN is:", "opts": ["Propanenitrile", "Butanenitrile", "Ethane", "No reaction"], "ans": "Propanenitrile", "type": "mc", "diff": 2},
        ],
        'HaloArenes': [
            {"q": "Chlorobenzene undergoes nucleophilic aromatic substitution when:", "opts": ["Strong electron-withdrawing groups present", "Any halogen present", "Only with NaOH", "With heat only"], "ans": "Strong electron-withdrawing groups present", "type": "mc", "diff": 3},
            {"q": "The benzyne mechanism involves:", "opts": ["Elimination-addition", "SN1", "SN2", "Free radical"], "ans": "Elimination-addition", "type": "mc", "diff": 3},
            {"q": "T/F: Halogens are ortho-para directors but deactivators in electrophilic aromatic substitution.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 3},
            {"q": "Nitration of chlorobenzene gives mainly:", "opts": ["Ortho and para nitrochlorobenzene", "Meta", "Only ortho", "Only para"], "ans": "Ortho and para nitrochlorobenzene", "type": "mc", "diff": 3},
            {"q": "Which halide undergoes SNAr fastest?", "opts": ["Chlorobenzene", "2,4-dinitrochlorobenzene", "Bromobenzene", "Iodobenzene"], "ans": "2,4-dinitrochlorobenzene", "type": "mc", "diff": 3},
            {"q": "T/F: Aryl halides do not undergo SN2 reactions under normal conditions.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "The directivity of halogen substituent is:", "opts": ["Ortho-para directing", "Meta directing", "No directing", "Para only"], "ans": "Ortho-para directing", "type": "mc", "diff": 2},
            {"q": "Which aryl halide undergoes coupling with Mg to form Grignard?", "opts": ["Chlorobenzene", "Only activated halides", "Usually not with aryl halides", "All aryl halides"], "ans": "Usually not with aryl halides", "type": "mc", "diff": 3},
            {"q": "Fill in: Nucleophilic aromatic substitution requires a(n) _____ group ortho/para to the leaving group.", "opts": ["Electron-withdrawing", "Electron-donating", "Alkyl", "None"], "ans": "Electron-withdrawing", "type": "fib", "diff": 3},
            {"q": "T/F: Aryl halides are less reactive than alkyl halides toward nucleophilic substitution.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
        ],
        'Nuclear Chemistry': [
            {"q": "In alpha decay, the mass number:", "opts": ["Decreases by 4", "Increases by 4", "Decreases by 2", "Stays the same"], "ans": "Decreases by 4", "type": "mc", "diff": 1},
            {"q": "Beta decay involves emission of:", "opts": ["Electron", "Helium nucleus", "Gamma ray", "Neutron"], "ans": "Electron", "type": "mc", "diff": 1},
            {"q": "Carbon-14 dating relies on:", "opts": ["Half-life of C-14", "Chemical reactivity", "Mass number", "Atomic number"], "ans": "Half-life of C-14", "type": "mc", "diff": 2},
            {"q": "T/F: Nuclear fission is used in nuclear power plants.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "The SI unit of radioactivity is:", "opts": ["Becquerel", "Curie", "Rutherford", "Gray"], "ans": "Becquerel", "type": "mc", "diff": 1},
            {"q": "In nuclear fusion,:", "opts": ["Light nuclei combine", "Heavy nuclei split", "Electrons combine", "Neutrons split"], "ans": "Light nuclei combine", "type": "mc", "diff": 1},
            {"q": "Which equation correctly represents alpha decay of U-238?", "opts": ["²³⁸U → ²³⁴Th + ⁴He", "²³⁸U → ²³⁶Th + ²He", "²³⁸U → ²³⁴Pa + ⁴He", "²³⁸U → ²³⁹Th + ⁰e"], "ans": "²³⁸U → ²³⁴Th + ⁴He", "type": "mc", "diff": 2},
            {"q": "Fill in: The half-life formula for first-order decay is t₁/₂ = _____ / λ.", "opts": ["ln(2)", "ln(10)", "2", "e"], "ans": "ln(2)", "type": "fib", "diff": 2},
            {"q": "T/F: Gamma rays have no mass and no charge.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "Nuclear power plants use _____ to control chain reactions.", "opts": ["Control rods", "Moderators", "Both A and B", "Neither"], "ans": "Both A and B", "type": "mc", "diff": 2},
            {"q": "Which isotope is used in medical imaging (PET)?", "opts": ["Fluorine-18", "Carbon-14", "Uranium-235", "Thorium-232"], "ans": "Fluorine-18", "type": "mc", "diff": 2},
            {"q": "T/F: Cobalt-60 is used in radiotherapy.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "The energy released in nuclear reactions comes from:", "opts": ["Mass defect (E=mc²)", "Chemical bonds", "Electron transitions", "Photons only"], "ans": "Mass defect (E=mc²)", "type": "mc", "diff": 2},
            {"q": "Fill in: Radiocarbon dating was developed by _____ in 1949.", "opts": ["Willard Libby", "Marie Curie", "Henri Becquerel", "Ernest Rutherford"], "ans": "Willard Libby", "type": "fib", "diff": 2},
            {"q": "T/F: Nuclear fission produces radioactive waste.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
        ],
        'Phenol': [
            {"q": "Phenol is more acidic than ethanol because:", "opts": ["The phenoxide ion is resonance-stabilized", "It has an –OH group", "It is an aromatic compound", "It has a lower molecular weight"], "ans": "The phenoxide ion is resonance-stabilized", "type": "mc", "diff": 2},
            {"q": "The reaction of phenol with Br2 water gives:", "opts": ["2,4,6-tribromophenol", "Monobromophenol", "No reaction", "Phenyl bromide"], "ans": "2,4,6-tribromophenol", "type": "mc", "diff": 2},
            {"q": "T/F: Phenol gives a purple color with FeCl3.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 1},
            {"q": "The pKa of phenol is approximately:", "opts": ["10", "4", "7", "14"], "ans": "10", "type": "mc", "diff": 2},
            {"q": "Nitration of phenol gives:", "opts": ["Ortho and para nitrophenol", "Only meta", "Only ortho", "No reaction"], "ans": "Ortho and para nitrophenol", "type": "mc", "diff": 2},
            {"q": "Phenol undergoes electrophilic substitution because:", "opts": ["The –OH group donates electrons into the ring", "It is a withdrawing group", "It is a meta director", "It deactivates the ring"], "ans": "The –OH group donates electrons into the ring", "type": "mc", "diff": 2},
            {"q": "T/F: Phenol can be prepared from cumene hydroperoxide process.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "The Kolbe-Schmitt reaction produces:", "opts": ["Salicylic acid", "Acetophenone", "Benzoic acid", "Aniline"], "ans": "Salicylic acid", "type": "mc", "diff": 3},
            {"q": "Fill in: Phenol undergoes _____ bromination with Br2 without a catalyst.", "opts": ["No Lewis acid needed", "Lewis acid", "High temperature", "UV light"], "ans": "No Lewis acid needed", "type": "fib", "diff": 2},
            {"q": "T/F: Phenol is more reactive than benzene toward electrophilic substitution.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "Which of the following is an ortho/para director?", "opts": ["–OH", "–NO2", "–CN", "–COOH"], "ans": "–OH", "type": "mc", "diff": 2},
            {"q": "The Reimer-Tiemann reaction on phenol gives:", "opts": ["Salicylaldehyde", "Benzaldehyde", "Anisole", "Catechol"], "ans": "Salicylaldehyde", "type": "mc", "diff": 3},
        ],
        'Transition Metal': [
            {"q": "Which is not a transition metal?", "opts": ["Zinc", "Iron", "Copper", "Chromium"], "ans": "Zinc", "type": "mc", "diff": 2},
            {"q": "The color of [Cu(H2O)6]²⁺ is:", "opts": ["Blue", "Green", "Red", "Colorless"], "ans": "Blue", "type": "mc", "diff": 1},
            {"q": "Crystal Field Theory explains:", "opts": ["Color and magnetism of complexes", "Bond angles", "Molecular geometry", "Bond length"], "ans": "Color and magnetism of complexes", "type": "mc", "diff": 2},
            {"q": "A paramagnetic complex has:", "opts": ["Unpaired electrons", "All paired electrons", "No d-electrons", "Charge"], "ans": "Unpaired electrons", "type": "mc", "diff": 1},
            {"q": "Fill in: The number of d-electrons in Fe³⁺ is _____.", "opts": ["5", "6", "8", "3"], "ans": "5", "type": "fib", "diff": 2},
            {"q": "T/F: High-spin octahedral complexes have more unpaired electrons than low-spin.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "Which ligand is a strong field ligand?", "opts": ["CN⁻", "I⁻", "Br⁻", "Cl⁻"], "ans": "CN⁻", "type": "mc", "diff": 2},
            {"q": "The coordination number of [Fe(H2O)6]³⁺ is:", "opts": ["6", "4", "2", "8"], "ans": "6", "type": "mc", "diff": 1},
            {"q": "T/F: Transition metals form colored compounds due to d-d transitions.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "The oxidation state of Cr in K2Cr2O7 is:", "opts": ["+6", "+3", "+7", "+5"], "ans": "+6", "type": "mc", "diff": 2},
            {"q": "Which is an example of a chelating agent?", "opts": ["EDTA", "Cl⁻", "H2O", "NH3"], "ans": "EDTA", "type": "mc", "diff": 2},
            {"q": "T/F: The crystal field splitting energy (Δo) increases across a period.", "opts": ["True", "False"], "ans": "True", "type": "tf", "diff": 2},
            {"q": "Which metal forms a blue precipitate with NaOH that dissolves in excess?", "opts": ["Cu²⁺", "Fe³⁺", "Zn²⁺", "Al³⁺"], "ans": "Cu²⁺", "type": "mc", "diff": 2},
        ]
    }
    for topic_name, questions in topics.items():
        for question in questions:
            q.append({
                "text": question["q"],
                "options": question["opts"],
                "correct_answer": question["ans"],
                "question_type": question["type"],
                "topic": topic_name,
                "difficulty": question["diff"],
                "id": len(q) + 1
            })
    return q

def get_topic_distribution(total=100):
    dist = {}
    topics = ['Alcohol', 'Chemical Kinetics', 'Electrochemistry', 'Ether', 'Haloalkanes', 'HaloArenes', 'Nuclear Chemistry', 'Phenol', 'Transition Metal']
    base = total // len(topics)
    extra = total % len(topics)
    for i, t in enumerate(topics):
        dist[t] = base + (1 if i < extra else 0)
    return dist
