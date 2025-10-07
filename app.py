import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Configuration de la page
st.set_page_config(
    page_title="Éligibilité IFS Food v8",
    page_icon="✅",
    layout="wide"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 20px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        padding: 20px;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffc107;
    }
    .danger-box {
        padding: 20px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation de l'état de session
if 'etape' not in st.session_state:
    st.session_state.etape = 1
if 'reponses' not in st.session_state:
    st.session_state.reponses = {}

# Titre principal
st.title("🎯 Outil d'Éligibilité IFS Food Version 8")
st.markdown("*Évaluez rapidement si votre entreprise est prête pour la certification IFS Food v8*")
st.markdown("---")

# Définition des questions par catégorie
QUESTIONS = {
    "informations": {
        "titre": "📋 Informations Générales",
        "questions": [
            {
                "id": "nom_entreprise",
                "question": "Nom de l'entreprise",
                "type": "text",
                "obligatoire": True
            },
            {
                "id": "activite",
                "question": "Type d'activité",
                "type": "select",
                "options": ["Transformation de produits alimentaires", "Conditionnement de produits nus", "Production de produits combinés", "Autre"],
                "obligatoire": True
            },
            {
                "id": "nb_employes",
                "question": "Nombre d'employés",
                "type": "number",
                "obligatoire": True
            },
            {
                "id": "production_annee",
                "question": "Depuis combien de temps l'entreprise est-elle en production ?",
                "type": "select",
                "options": ["Moins de 3 mois", "3-6 mois", "6-12 mois", "Plus d'un an"],
                "points": [0, 5, 10, 15],
                "obligatoire": True
            }
        ]
    },
    "prerequis_ko": {
        "titre": "⚠️ Prérequis Essentiels (Exigences KO)",
        "description": "Ces éléments sont **OBLIGATOIRES** pour la certification IFS Food",
        "questions": [
            {
                "id": "ko_1",
                "question": "Avez-vous un responsable qualité/sécurité alimentaire identifié avec des responsabilités documentées ?",
                "reference": "KO n°1 - 1.2.1",
                "type": "radio",
                "options": ["Oui", "Non"],
                "points": [100, 0],
                "ko": True
            },
            {
                "id": "ko_2",
                "question": "Disposez-vous d'un système de surveillance documenté pour chaque CCP (Point Critique de Contrôle) ?",
                "reference": "KO n°2 - 2.3.9.1",
                "type": "radio",
                "options": ["Oui, tous les CCP sont surveillés", "Partiellement", "Non", "Nous n'avons pas de CCP identifiés"],
                "points": [100, 30, 0, 0],
                "ko": True
            },
            {
                "id": "ko_3",
                "question": "Avez-vous des exigences d'hygiène personnelle documentées et appliquées par tous ?",
                "reference": "KO n°3 - 3.2.2",
                "type": "radio",
                "options": ["Oui", "Partiellement", "Non"],
                "points": [100, 40, 0],
                "ko": True
            },
            {
                "id": "ko_4",
                "question": "Les accords avec les clients (recettes, procédés, conditionnement) sont-ils respectés ?",
                "reference": "KO n°4 - 4.1.3",
                "type": "radio",
                "options": ["Oui, systématiquement", "La plupart du temps", "Non applicable - pas d'accords clients", "Non"],
                "points": [100, 50, 100, 0],
                "ko": True
            },
            {
                "id": "ko_5",
                "question": "Disposez-vous de spécifications documentées pour toutes vos matières premières ?",
                "reference": "KO n°5 - 4.2.1.3",
                "type": "radio",
                "options": ["Oui, pour toutes", "Pour la majorité", "Pour quelques-unes", "Non"],
                "points": [100, 50, 20, 0],
                "ko": True
            },
            {
                "id": "ko_6",
                "question": "Avez-vous des procédures pour empêcher la contamination par des corps étrangers ?",
                "reference": "KO n°6 - 4.12.1",
                "type": "radio",
                "options": ["Oui, documentées et appliquées", "Oui, mais non documentées", "Partiellement", "Non"],
                "points": [100, 40, 20, 0],
                "ko": True
            },
            {
                "id": "ko_7",
                "question": "Avez-vous un système de traçabilité documenté (du fournisseur au client) ?",
                "reference": "KO n°7 - 4.18.1",
                "type": "radio",
                "options": ["Oui, complet et testé", "Oui, mais non testé", "Partiellement", "Non"],
                "points": [100, 60, 20, 0],
                "ko": True
            },
            {
                "id": "ko_8",
                "question": "Réalisez-vous des audits internes couvrant toutes les exigences IFS au moins une fois par an ?",
                "reference": "KO n°8 - 5.1.1",
                "type": "radio",
                "options": ["Oui, régulièrement", "Occasionnellement", "Non, jamais"],
                "points": [100, 30, 0],
                "ko": True
            },
            {
                "id": "ko_9",
                "question": "Avez-vous une procédure documentée pour gérer les rappels et retraits de produits ?",
                "reference": "KO n°9 - 5.9.1",
                "type": "radio",
                "options": ["Oui, documentée et testée", "Oui, mais non testée", "Non"],
                "points": [100, 50, 0],
                "ko": True
            },
            {
                "id": "ko_10",
                "question": "Mettez-vous en place des actions correctives pour éviter la réapparition des non-conformités ?",
                "reference": "KO n°10 - 5.11.3",
                "type": "radio",
                "options": ["Oui, systématiquement", "Parfois", "Non"],
                "points": [100, 40, 0],
                "ko": True
            }
        ]
    },
    "systeme_qualite": {
        "titre": "📊 Système de Management Qualité",
        "questions": [
            {
                "id": "politique_qualite",
                "question": "Disposez-vous d'une politique qualité et sécurité alimentaire documentée ?",
                "reference": "1.1.1",
                "type": "radio",
                "options": ["Oui, communiquée à tous", "Oui, mais non communiquée", "Non"],
                "points": [20, 10, 0]
            },
            {
                "id": "revue_direction",
                "question": "Réalisez-vous une revue de direction au moins une fois par an ?",
                "reference": "1.3.1",
                "type": "radio",
                "options": ["Oui, régulièrement", "Occasionnellement", "Non"],
                "points": [20, 10, 0]
            },
            {
                "id": "haccp",
                "question": "Avez-vous un plan HACCP complet et documenté ?",
                "reference": "2.2.1.1",
                "type": "radio",
                "options": ["Oui, conforme Codex Alimentarius", "Oui, mais incomplet", "En cours d'élaboration", "Non"],
                "points": [30, 15, 5, 0]
            },
            {
                "id": "gestion_doc",
                "question": "Avez-vous un système de gestion documentaire (procédures, enregistrements) ?",
                "reference": "2.1.1",
                "type": "radio",
                "options": ["Oui, système complet", "Partiellement", "Non"],
                "points": [15, 8, 0]
            },
            {
                "id": "reclamations",
                "question": "Avez-vous une procédure de gestion des réclamations clients ?",
                "reference": "5.8.1",
                "type": "radio",
                "options": ["Oui, documentée et appliquée", "Oui, mais informelle", "Non"],
                "points": [15, 7, 0]
            }
        ]
    },
    "ressources": {
        "titre": "👥 Ressources et Compétences",
        "questions": [
            {
                "id": "formation",
                "question": "Disposez-vous d'un programme de formation documenté pour le personnel ?",
                "reference": "3.3.1",
                "type": "radio",
                "options": ["Oui, avec plan annuel", "Oui, mais informel", "Non"],
                "points": [20, 10, 0]
            },
            {
                "id": "formation_haccp",
                "question": "Votre personnel clé a-t-il été formé à l'HACCP ?",
                "reference": "2.3.1.2",
                "type": "radio",
                "options": ["Oui, formation externe certifiée", "Oui, formation interne", "Non"],
                "points": [15, 10, 0]
            },
            {
                "id": "installations",
                "question": "Vos installations sont-elles adaptées à la production alimentaire (locaux, équipements) ?",
                "reference": "4.9.1.1",
                "type": "radio",
                "options": ["Oui, conformes", "Partiellement conformes", "Non conformes"],
                "points": [20, 10, 0]
            },
            {
                "id": "nettoyage",
                "question": "Avez-vous un plan de nettoyage et désinfection documenté ?",
                "reference": "4.10.1",
                "type": "radio",
                "options": ["Oui, documenté et validé", "Oui, mais non validé", "Non"],
                "points": [15, 8, 0]
            }
        ]
    },
    "controles": {
        "titre": "🔬 Contrôles et Analyses",
        "questions": [
            {
                "id": "analyses",
                "question": "Réalisez-vous des analyses de produits (internes ou externes) ?",
                "reference": "5.6.1",
                "type": "radio",
                "options": ["Oui, plan d'analyses complet", "Oui, analyses ponctuelles", "Non"],
                "points": [20, 10, 0]
            },
            {
                "id": "maitrise_quantite",
                "question": "Avez-vous un système de maîtrise des quantités ?",
                "reference": "5.5.1",
                "type": "radio",
                "options": ["Oui", "Partiellement", "Non"],
                "points": [15, 8, 0]
            },
            {
                "id": "etalonnage",
                "question": "Vos appareils de mesure sont-ils étalonnés régulièrement ?",
                "reference": "5.4.2",
                "type": "radio",
                "options": ["Oui, programme d'étalonnage", "Occasionnellement", "Non"],
                "points": [15, 5, 0]
            },
            {
                "id": "produits_nc",
                "question": "Avez-vous une procédure pour gérer les produits non conformes ?",
                "reference": "5.10.1",
                "type": "radio",
                "options": ["Oui, documentée", "Oui, mais informelle", "Non"],
                "points": [15, 7, 0]
            }
        ]
    }
}

def calculer_score(reponses):
    """Calcule le score total et par catégorie"""
    score_total = 0
    score_max = 0
    scores_categories = {}
    ko_manquants = []
    
    for categorie, data in QUESTIONS.items():
        if categorie == "informations":
            continue
            
        score_cat = 0
        max_cat = 0
        
        for q in data["questions"]:
            if q["type"] in ["radio", "select"] and "points" in q:
                max_points = max(q["points"])
                max_cat += max_points
                
                if q["id"] in reponses:
                    idx = q["options"].index(reponses[q["id"]])
                    points = q["points"][idx]
                    score_cat += points
                    
                    # Vérifier les KO
                    if q.get("ko", False) and points < 100:
                        ko_manquants.append({
                            "question": q["question"],
                            "reference": q.get("reference", ""),
                            "reponse": reponses[q["id"]]
                        })
        
        if max_cat > 0:
            scores_categories[categorie] = {
                "score": score_cat,
                "max": max_cat,
                "pourcentage": (score_cat / max_cat) * 100
            }
            score_total += score_cat
            score_max += max_cat
    
    pourcentage_total = (score_total / score_max * 100) if score_max > 0 else 0
    
    return {
        "score": score_total,
        "max": score_max,
        "pourcentage": pourcentage_total,
        "categories": scores_categories,
        "ko_manquants": ko_manquants
    }

def determiner_eligibilite(resultats):
    """Détermine l'éligibilité basée sur le score"""
    pourcentage = resultats["pourcentage"]
    ko_manquants = len(resultats["ko_manquants"])
    
    if ko_manquants > 0:
        return {
            "statut": "NON_ELIGIBLE",
            "niveau": "❌ NON ÉLIGIBLE",
            "couleur": "danger",
            "message": f"**{ko_manquants} exigence(s) KO manquante(s)**. Ces prérequis essentiels sont OBLIGATOIRES pour la certification IFS Food."
        }
    elif pourcentage >= 90:
        return {
            "statut": "ELIGIBLE",
            "niveau": "✅ ÉLIGIBLE",
            "couleur": "success",
            "message": "Votre entreprise semble prête pour entamer le processus de certification IFS Food v8."
        }
    elif pourcentage >= 75:
        return {
            "statut": "ELIGIBLE_RESERVE",
            "niveau": "⚠️ ÉLIGIBLE AVEC RÉSERVES",
            "couleur": "warning",
            "message": "Votre entreprise a les bases nécessaires, mais des améliorations sont recommandées avant l'audit."
        }
    elif pourcentage >= 50:
        return {
            "statut": "AMELIORATIONS_REQUISES",
            "niveau": "⚠️ AMÉLIORATIONS IMPORTANTES REQUISES",
            "couleur": "warning",
            "message": "Une mise à niveau significative de votre système qualité est nécessaire avant de pouvoir envisager la certification."
        }
    else:
        return {
            "statut": "NON_ELIGIBLE",
            "niveau": "❌ NON ÉLIGIBLE",
            "couleur": "danger",
            "message": "Les prérequis fondamentaux ne sont pas en place. Un accompagnement est fortement recommandé."
        }

def afficher_question(question, categorie_id):
    """Affiche une question selon son type"""
    key = f"{categorie_id}_{question['id']}"
    
    # Affichage de la question avec référence
    st.markdown(f"**{question['question']}**")
    if "reference" in question:
        st.caption(f"📖 Référence IFS: {question['reference']}")
    
    # Gestion selon le type de question
    if question["type"] == "text":
        valeur = st.text_input("", key=key, label_visibility="collapsed")
    elif question["type"] == "number":
        valeur = st.number_input("", min_value=0, key=key, label_visibility="collapsed")
    elif question["type"] == "select":
        valeur = st.selectbox("", question["options"], key=key, label_visibility="collapsed")
    elif question["type"] == "radio":
        valeur = st.radio("", question["options"], key=key, label_visibility="collapsed")
    else:
        valeur = None
    
    if valeur:
        st.session_state.reponses[question["id"]] = valeur
    
    st.markdown("---")

def afficher_resultats(resultats, eligibilite, reponses):
    """Affiche les résultats de l'évaluation"""
    st.markdown("## 📊 Résultats de l'Évaluation")
    
    # Informations entreprise
    with st.expander("ℹ️ Informations de l'entreprise", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Entreprise:** {reponses.get('nom_entreprise', 'N/A')}")
            st.write(f"**Activité:** {reponses.get('activite', 'N/A')}")
        with col2:
            st.write(f"**Nombre d'employés:** {reponses.get('nb_employes', 'N/A')}")
            st.write(f"**Durée de production:** {reponses.get('production_annee', 'N/A')}")
    
    st.markdown("---")
    
    # Résultat principal
    st.markdown(f"""
    <div class='{eligibilite["couleur"]}-box'>
        <h2 style='margin:0;'>{eligibilite["niveau"]}</h2>
        <p style='font-size:24px; margin:10px 0;'><strong>Score: {resultats['pourcentage']:.1f}%</strong> ({resultats['score']}/{resultats['max']} points)</p>
        <p style='margin:0;'>{eligibilite["message"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Exigences KO manquantes
    if resultats["ko_manquants"]:
        st.markdown("### 🚨 Exigences KO Manquantes (CRITIQUE)")
        st.error("Les exigences suivantes sont **OBLIGATOIRES** et doivent être mises en place avant la certification:")
        
        for i, ko in enumerate(resultats["ko_manquants"], 1):
            st.markdown(f"""
            **{i}. {ko['question']}**  
            📖 *Référence: {ko['reference']}*  
            ➡️ Votre réponse: *{ko['reponse']}*
            """)
            st.markdown("---")
    
    # Scores par catégorie
    st.markdown("### 📈 Détail par Catégorie")
    
    for cat_id, cat_data in resultats["categories"].items():
        cat_info = QUESTIONS[cat_id]
        pourcentage = cat_data["pourcentage"]
        
        # Couleur selon le score
        if pourcentage >= 80:
            couleur = "🟢"
        elif pourcentage >= 50:
            couleur = "🟡"
        else:
            couleur = "🔴"
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"{couleur} **{cat_info['titre']}**")
        with col2:
            st.markdown(f"**{pourcentage:.0f}%**")
        
        st.progress(pourcentage / 100)
        st.caption(f"{cat_data['score']}/{cat_data['max']} points")
        st.markdown("")
    
    # Recommandations
    st.markdown("---")
    st.markdown("### 💡 Recommandations")
    
    if eligibilite["statut"] == "ELIGIBLE":
        st.success("""
        **Prochaines étapes recommandées:**
        1. ✅ Contactez notre organisme pour planifier l'audit initial
        2. ✅ Préparez la documentation demandée
        3. ✅ Désignez un interlocuteur dédié
        4. ✅ Planifiez l'audit (délai recommandé: 2-3 mois)
        """)
    
    elif eligibilite["statut"] == "ELIGIBLE_RESERVE":
        st.warning("""
        **Actions recommandées avant l'audit:**
        1. ⚠️ Renforcez les points faibles identifiés
        2. ⚠️ Complétez la documentation manquante
        3. ⚠️ Envisagez un pré-audit (optionnel)
        4. ⚠️ Formez votre équipe aux exigences IFS
        5. ⚠️ Délai recommandé avant audit: 3-6 mois
        """)
    
    else:
        st.error("""
        **Plan d'action recommandé:**
        1. ❌ Mise en place des prérequis essentiels (exigences KO)
        2. ❌ Développement du système de management qualité
        3. ❌ Formation de l'équipe
        4. ❌ Accompagnement par un consultant IFS (fortement recommandé)
        5. ❌ Délai minimum avant certification: 6-12 mois
        """)
    
    # Bouton de téléchargement du rapport
    st.markdown("---")
    
    rapport_json = {
        "date_evaluation": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "entreprise": reponses.get("nom_entreprise", "N/A"),
        "resultats": {
            "score_total": f"{resultats['pourcentage']:.1f}%",
            "eligibilite": eligibilite["niveau"],
            "statut": eligibilite["statut"]
        },
        "categories": {
            cat_id: {
                "titre": QUESTIONS[cat_id]["titre"],
                "score": f"{data['pourcentage']:.0f}%"
            }
            for cat_id, data in resultats["categories"].items()
        },
        "ko_manquants": resultats["ko_manquants"]
    }
    
    st.download_button(
        label="📥 Télécharger le rapport (JSON)",
        data=json.dumps(rapport_json, indent=2, ensure_ascii=False),
        file_name=f"evaluation_ifs_{reponses.get('nom_entreprise', 'entreprise').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json"
    )

# ========== INTERFACE PRINCIPALE ==========

# Barre de progression
categories_list = list(QUESTIONS.keys())
total_etapes = len(categories_list) + 1  # +1 pour la page de résultats

# Vérifier que l'étape est valide
if st.session_state.etape > total_etapes:
    st.session_state.etape = total_etapes
if st.session_state.etape < 1:
    st.session_state.etape = 1

progress = (st.session_state.etape - 1) / (total_etapes - 1) if total_etapes > 1 else 0
st.progress(progress)
st.caption(f"Étape {st.session_state.etape}/{total_etapes}")

# Navigation
if st.session_state.etape <= len(categories_list):
    # Pages de questionnaire
    categorie_actuelle = categories_list[st.session_state.etape - 1]
    cat_data = QUESTIONS[categorie_actuelle]
    
    st.markdown(f"## {cat_data['titre']}")
    
    if "description" in cat_data:
        st.info(cat_data["description"])
    
    st.markdown("---")
    
    # Affichage des questions
    for question in cat_data["questions"]:
        afficher_question(question, categorie_actuelle)
    
    # Boutons de navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.session_state.etape > 1:
            if st.button("⬅️ Précédent"):
                st.session_state.etape -= 1
                st.rerun()
    
    with col3:
        if st.session_state.etape < len(categories_list):
            if st.button("Suivant ➡️"):
                st.session_state.etape += 1
                st.rerun()
        else:
            if st.button("🎯 Voir les résultats"):
                st.session_state.etape += 1
                st.rerun()

else:
    # Page de résultats
    resultats = calculer_score(st.session_state.reponses)
    eligibilite = determiner_eligibilite(resultats)
    afficher_resultats(resultats, eligibilite, st.session_state.reponses)
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Retour au questionnaire"):
            st.session_state.etape = len(categories_list)
            st.rerun()
    
    with col2:
        if st.button("🔄 Nouvelle évaluation"):
            st.session_state.etape = 1
            st.session_state.reponses = {}
            st.rerun()

# Footer
st.markdown("---")
st.caption("🔒 Cet outil est fourni à titre indicatif. Une évaluation complète sera réalisée lors de l'audit officiel.")
st.caption("📧 Contact: contact@votre-organisme.fr | 📞 01 23 45 67 89")
