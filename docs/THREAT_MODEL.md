# Threat Model

## Assets

- Comptes utilisateurs
- JWT et sessions
- Photos repas/progression
- Donnees sante et fitness
- Base PostgreSQL
- Cle Gemini API

## Menaces

- Account takeover
- IDOR/BOLA
- XSS
- Injection SQL
- Prompt injection
- Data leakage
- Upload abuse (polyglot, malware-like payload)
- API abuse / scraping
- Secret leakage

## Mitigations

- JWT validation stricte (iss/aud/exp/nbf/iat/signature)
- Ownership checks par user_id sur toutes les ressources privees
- Validation Pydantic stricte et bornes de payload
- ORM SQLAlchemy uniquement, aucune requete SQL brute utilisateur
- Rate limiting par categorie et identite
- Upload validation + Pillow re-encode + EXIF strip
- CSP + headers securite + frame-ancestors none
- CORS allowlist stricte
- Logging redaction + request_id
- RLS Supabase + Storage policies privees

## Residual Risks

- Token en localStorage reste plus expose a XSS qu'un cookie HttpOnly.
- Politiques Supabase doivent etre appliquees en infra (scripts fournis mais action manuelle).
- npm/pip ecosystem peut conserver des CVE transitives necessitant upgrades iteratifs.
