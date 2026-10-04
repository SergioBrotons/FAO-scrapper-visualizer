#!/usr/bin/env python3
"""Sanitize tone of voice and enforce strict NO EMOJIS rule across map_builder.py."""

import re
from pathlib import Path

MAP_BUILDER = Path("src/fao_transactions/visualization/map_builder.py")
content = MAP_BUILDER.read_text(encoding="utf-8")

# Specific replacements for terminology and emojis
replacements = [
    # Top-level buttons and labels
    ('<span style="color:#06b6d4;">⚔️</span> Duel Face-à-Face', 'Comparateur Bilatéral'),
    ('⚔️ Duel Face-à-Face', 'Comparateur Bilatéral'),
    ('⚔️ Duel', 'Comparer'),
    ('⚔️ DUEL ACTIF', 'ANALYSE COMPARATIVE BILATÉRALE'),
    ('⚔️ DUEL :', 'COMPARAISON :'),
    ('⚔️ Duel d\'Agences — Comparateur Face-à-Face & Conflit Territorial', 'ANALYSE COMPARATIVE BILATÉRALE — RECOUVREMENT TERRITORIAL ET PERFORMANCE'),
    ('📍 Projeter le Duel sur la Carte', 'Projeter la comparaison sur la carte'),
    ('🗺️ Projeter les 2 Réseaux sur la Carte', 'Afficher les deux réseaux sur la carte'),
    ('📊 Comparateur', 'Fiche comparative'),
    ('Quitter le mode Duel', 'Quitter la comparaison'),
    ('resetAgencyDuelMap()', 'resetAgencyDuelMap()'),
    ('Rivalité Territoriale EXTRÊME', 'Recouvrement Territorial Élevé'),
    ('Rivalité Territoriale FORTE', 'Recouvrement Territorial Modéré'),
    ('Rivalité Territoriale MODÉRÉE', 'Recouvrement Territorial Faible'),
    ('Rivalité Territoriale ${rivalryLevel}', 'Recouvrement Territorial ${rivalryLevel}'),
    ('rivalryLevel = overlapPct >= 50 ? \'EXTRÊME\' : (overlapPct >= 25 ? \'FORTE\' : \'MODÉRÉE\');',
     'rivalryLevel = overlapPct >= 50 ? \'ÉLEVÉ\' : (overlapPct >= 25 ? \'MODÉRÉ\' : \'FAIBLE\');'),

    # Vault & Privacy buttons
    ('<span id="vaultToggleIcon">🔒</span> <span id="vaultToggleLabel">nLPD Conforme</span>',
     '<span id="vaultToggleLabel">nLPD Conforme</span>'),
    ('iconEl.textContent = \'🔓\';', 'if (iconEl) iconEl.textContent = \'\';'),
    ('iconEl.textContent = \'🔒\';', 'if (iconEl) iconEl.textContent = \'\';'),
    ('showToastNotification(\'🔒 Mode public nLPD réactivé', 'showToastNotification(\'Mode public nLPD réactivé'),
    ('showToastNotification(\'🔓 Mode Interne Souverain déverrouillé', 'showToastNotification(\'Mode Interne Souverain déverrouillé'),
    ('span style="font-size: 16px;">🔐</span>', ''),
    ('span style="font-size: 14px;">🔒</span>', ''),
    ('<span>🔒</span> LinkedIn', '<span></span> LinkedIn'),
    ('🔒 LinkedIn : En cours de vérification', 'LinkedIn : Vérification en cours'),
    ('🔒 LinkedIn : En vérification', 'LinkedIn : En cours d\'audit'),
    ('💡 <strong>Accès direct par URL :</strong>', '<strong>Accès direct par URL :</strong>'),
    ('👁️ Révéler', 'Révéler'),
    ('🏢 Personne Morale (RC)', 'Personne Morale (RC)'),

    # Velocity headers
    ('⚡ Vélocité Commerciale & Momentum Notarié', 'VÉLOCITÉ TRANSACTIONNELLE & MOMENTUM NOTARIÉ'),
    ('⚡ Score de Vélocité', 'Score de Vélocité'),
    ('<span>⚡ Vélocité Commerciale & Momentum Notarié (Public Data)</span>', '<span>VÉLOCITÉ TRANSACTIONNELLE & MOMENTUM NOTARIÉ (DONNÉES OFFICIELLES)</span>'),
]

for old, new in replacements:
    if old in content:
        content = content.replace(old, new)

print("[OK] Replacements applied.")

# General purge of any remaining emoji characters
# Ranges: \U00010000-\U0010ffff, \u2600-\u26ff, \u2700-\u27bf, \u2b50-\u2b55
def remove_emojis(match):
    ch = match.group(0)
    # preserve safe arrows and math symbols if any
    if ch in ['\u2197', '\u2192', '\u2198', '\u2190', '\u2191', '\u2193']: # arrows ↗ → ↘
        return ch
    if ch in ['\u2713', '\u2715']: # checkmark ✓ and cross ✕
        return ch
    return ''

emoji_regex = re.compile(r'[\U00010000-\U0010ffff]|[\u2600-\u26ff]|[\u2700-\u27bf]|[\u2b50-\u2b55]')
content = emoji_regex.sub(remove_emojis, content)

MAP_BUILDER.write_text(content, encoding="utf-8")
print("[OK] Finished sanitizing map_builder.py.")
