# Security Policy

## Security Architecture

- Backend en point de controle unique pour auth, authorizations et acces IA.
- Validation stricte Pydantic sur toutes les entrees API.
- Ownership systematique par user_id sur les ressources privees.
- Headers de securite HTTP actifs (CSP, HSTS, nosniff, referrer, permissions).
- Rate limiting par categorie (auth, api, upload, IA) avec cle IP + identite.

## Secrets

- Aucun secret ne doit etre committe.
- Utiliser uniquement des variables d'environnement.
- NEXT_PUBLIC ne doit jamais contenir de secret.
- Si une cle a fuite dans l'historique Git: revoquer et regenirer immediatement.

## Auth

- Validation JWT stricte: signature, algorithme, issuer, audience, exp, nbf, iat.
- get_current_user est obligatoire sur routes privees.
- user_id ne vient jamais du frontend.

## Supabase RLS and Storage

- Activer RLS pour toutes les tables utilisateur.
- Policies owner-only pour read/write/delete.
- Buckets storage prives.
- Objects stockes sous user_id/uuid.ext
- Utiliser signed URLs temporaires, jamais d'URL publique permanente.

## Upload Security

- MIME whitelist stricte: JPEG, PNG, WEBP.
- Taille max 10MB.
- Verification et re-encodage Pillow, suppression EXIF.
- Blocage de dimensions excesives et fichiers invalides.

## Incident Response

1. Identifier la portee.
2. Revoquer tous les tokens/cles potentiellement exposes.
3. Corriger et deployer.
4. Auditer les acces et notifier les utilisateurs impactes.
5. Ajouter regression tests securite.

## Vulnerability Reporting

- Signaler toute vulnérabilité de facon privée aux maintainers du projet.
- Inclure: endpoint, vecteur, impact, preuve de concept minimale, suggestion de patch.

## Production Checklist

- DEBUG=false
- OpenAPI desactive ou protege
- CORS sur allowlist stricte
- RLS active et testee
- Service account Cloud Run least privilege
- Secrets via Secret Manager
- Logs sans donnees sensibles
- Backups chiffrés et non publics
