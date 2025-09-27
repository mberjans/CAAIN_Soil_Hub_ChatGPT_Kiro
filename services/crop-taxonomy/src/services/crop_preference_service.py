"""
Crop Preference Service

Manages farmer crop preference profiles, supports preference learning,
and provides conflict-aware preference responses.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from importlib import import_module
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)

_try_database_imports: List[str] = [
    'src.database.crop_taxonomy_db',
    '..database.crop_taxonomy_db',
    'database.crop_taxonomy_db'
]

CropTaxonomyDatabase = None
for _candidate in _try_database_imports:
    try:  # pragma: no cover - dynamic import pattern
        if _candidate.startswith('..'):
            module = import_module(_candidate, package=__package__)
        else:
            module = import_module(_candidate)
        CropTaxonomyDatabase = getattr(module, 'CropTaxonomyDatabase', None)
        if CropTaxonomyDatabase is not None:
            break
    except ImportError:
        continue

_try_model_imports: List[Tuple[str, str]] = [
    ('src.models.preference_models', 'PreferenceProfile'),
    ('src.models.preference_models', 'PreferenceUpdateRequest'),
    ('src.models.preference_models', 'PreferenceProfileResponse'),
    ('src.models.preference_models', 'PreferenceLearningRequest'),
    ('src.models.preference_models', 'PreferenceWeight'),
    ('src.models.preference_models', 'PreferenceConstraint'),
    ('src.models.preference_models', 'PreferenceType'),
    ('src.models.preference_models', 'PreferenceDimension'),
    ('src.models.preference_models', 'PreferenceConfidence'),
    ('src.models.preference_models', 'ConstraintType'),
    ('src.models.preference_models', 'PreferenceSignal'),
    ('src.models.preference_models', 'ManagementStyle'),
    ('src.models.preference_models', 'RiskTolerance')
]

PreferenceProfile = None
PreferenceUpdateRequest = None
PreferenceProfileResponse = None
PreferenceLearningRequest = None
PreferenceWeight = None
PreferenceConstraint = None
PreferenceType = None
PreferenceDimension = None
PreferenceConfidence = None
ConstraintType = None
PreferenceSignal = None
ManagementStyle = None
RiskTolerance = None

for _module_name, _attribute in _try_model_imports:
    try:
        module = import_module(_module_name)
        value = getattr(module, _attribute)
        globals()[_attribute] = value
    except ImportError:
        continue

CropFilteringAttributes = None
for _candidate_model in (
    'src.models.crop_filtering_models',
    '..models.crop_filtering_models',
    'models.crop_filtering_models'
):
    try:
        if _candidate_model.startswith('..'):
            module = import_module(_candidate_model, package=__package__)
        else:
            module = import_module(_candidate_model)
        CropFilteringAttributes = getattr(module, 'CropFilteringAttributes', None)
        if CropFilteringAttributes is not None:
            break
    except (ImportError, TypeError):
        continue


class CropPreferenceService:
    """Service managing farmer crop preference profiles and learning."""

    def __init__(self, database_url: Optional[str] = None):
        self.db = None
        self.database_available = False
        if CropTaxonomyDatabase is not None:
            try:
                self.db = CropTaxonomyDatabase(database_url)
                self.database_available = self.db.test_connection()
            except Exception as exc:
                logger.warning("Crop preference database unavailable: %s", exc)
                self.db = None
                self.database_available = False
        else:
            logger.warning("Crop preference database integration missing")

        self._memory_profiles: Dict[str, Dict[str, Any]] = {}
        self._signal_history: Dict[str, List[Dict[str, Any]]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_preference_profile(
        self,
        user_id: UUID,
        preference_type: Optional[PreferenceType] = None
    ) -> PreferenceProfileResponse:
        profile = await self._load_profile(user_id, preference_type)
        if profile is None:
            empty_profile = PreferenceProfile(
                preference_id=None,
                user_id=user_id,
                preference_type=preference_type or PreferenceType.USER_DEFINED,
                crop_categories=[],
                weights=[],
                constraints=[],
                market_focus=[],
                sustainability_focus=[],
            )
            profile = empty_profile
        conflict_notes = self._detect_conflicts(profile)
        sources = self._determine_sources()
        return PreferenceProfileResponse(
            profile=profile,
            sources=sources,
            derived_recommendations=self._derive_recommendations(profile),
            conflict_notes=conflict_notes
        )

    async def upsert_preference_profile(
        self,
        request: PreferenceUpdateRequest
    ) -> PreferenceProfileResponse:
        stored_profile = await self._store_profile(request)
        conflict_notes = self._detect_conflicts(stored_profile)
        sources = self._determine_sources()
        return PreferenceProfileResponse(
            profile=stored_profile,
            sources=sources,
            derived_recommendations=self._derive_recommendations(stored_profile),
            conflict_notes=conflict_notes
        )

    async def learn_preferences(
        self,
        request: PreferenceLearningRequest
    ) -> PreferenceProfileResponse:
        base_profile = await self._load_profile(request.user_id, None)
        if base_profile is None:
            base_profile = PreferenceProfile(
                preference_id=None,
                user_id=request.user_id,
                preference_type=PreferenceType.LEARNED,
                crop_categories=[],
                weights=[],
                constraints=[],
                market_focus=[],
                sustainability_focus=[],
                confidence=PreferenceConfidence.LOW
            )
        updated_profile = self._apply_signals(base_profile, request)
        update_request = PreferenceUpdateRequest(
            profile=updated_profile,
            replace_existing=False
        )
        resulting_profile = await self._store_profile(update_request)
        conflict_notes = self._detect_conflicts(resulting_profile)
        sources = self._determine_sources()
        return PreferenceProfileResponse(
            profile=resulting_profile,
            sources=sources,
            derived_recommendations=self._derive_recommendations(resulting_profile),
            conflict_notes=conflict_notes
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _load_profile(
        self,
        user_id: UUID,
        preference_type: Optional[PreferenceType]
    ) -> Optional[PreferenceProfile]:
        storage_record: Optional[Dict[str, Any]] = None
        if self.database_available and self.db is not None:
            try:
                type_value = preference_type.value if preference_type else None
                storage_record = self.db.get_preference_profile(user_id, type_value)
            except Exception as exc:
                logger.error("Database error loading preference profile: %s", exc)
        if storage_record is None:
            key = self._memory_key(user_id, preference_type.value if preference_type else None)
            storage_record = self._memory_profiles.get(key)
            if storage_record is None and preference_type is None:
                fallback_order = [
                    PreferenceType.USER_DEFINED.value,
                    PreferenceType.LEARNED.value,
                    PreferenceType.SYSTEM_SUGGESTED.value
                ]
                for fallback_type in fallback_order:
                    fallback_key = self._memory_key(user_id, fallback_type)
                    if fallback_key in self._memory_profiles:
                        storage_record = self._memory_profiles.get(fallback_key)
                        if storage_record is not None:
                            break
        if storage_record is None:
            return None
        return self._record_to_profile(storage_record)

    async def _store_profile(self, request: PreferenceUpdateRequest) -> PreferenceProfile:
        profile = request.profile
        storage_payload = self._profile_to_record(profile)
        storage_payload['profile_metadata'] = profile.metadata
        storage_payload['priority_notes'] = profile.priority_notes
        if self.database_available and self.db is not None:
            try:
                stored_record = self.db.upsert_preference_profile(
                    storage_payload,
                    replace_existing=request.replace_existing
                )
                return self._record_to_profile(stored_record)
            except Exception as exc:
                logger.error("Database error storing preference profile: %s", exc)
        key = self._memory_key(profile.user_id, profile.preference_type.value)
        aggregated = self._merge_memory_profile(key, storage_payload, request.replace_existing)
        return self._record_to_profile(aggregated)

    def _merge_memory_profile(
        self,
        key: str,
        payload: Dict[str, Any],
        replace_existing: bool
    ) -> Dict[str, Any]:
        existing = self._memory_profiles.get(key)
        if existing is None or replace_existing:
            record = {}
        else:
            record = {}
            for existing_key, existing_value in existing.items():
                record[existing_key] = existing_value
        for payload_key, payload_value in payload.items():
            record[payload_key] = payload_value
        if 'preference_id' not in record or record['preference_id'] is None:
            record['preference_id'] = str(uuid4())
        record['updated_at'] = datetime.utcnow().isoformat()
        if 'created_at' not in record or record.get('created_at') is None:
            record['created_at'] = datetime.utcnow().isoformat()
        self._memory_profiles[key] = record
        return record

    def _apply_signals(
        self,
        profile: PreferenceProfile,
        request: PreferenceLearningRequest
    ) -> PreferenceProfile:
        weights_map: Dict[str, PreferenceWeight] = {}
        for existing_weight in profile.weights:
            composite_key = self._weight_key(existing_weight.dimension.value, existing_weight.key)
            weights_map[composite_key] = existing_weight
        for signal in request.signals:
            self._store_signal_history(request.user_id, signal)
            dimension_value = self._resolve_dimension(signal.context)
            key_value = self._resolve_key(signal, dimension_value)
            composite_key = self._weight_key(dimension_value.value, key_value)
            if composite_key not in weights_map:
                new_weight = PreferenceWeight(
                    dimension=dimension_value,
                    key=key_value,
                    weight=max(signal.weight, 0.0)
                )
                weights_map[composite_key] = new_weight
            else:
                existing_weight = weights_map[composite_key]
                adjusted = (existing_weight.weight * request.decay_factor) + (signal.weight * request.learning_rate)
                if adjusted < 0.0:
                    adjusted = 0.0
                if adjusted > 1.0:
                    adjusted = 1.0
                weights_map[composite_key] = PreferenceWeight(
                    dimension=existing_weight.dimension,
                    key=existing_weight.key,
                    weight=adjusted
                )
        updated_weights: List[PreferenceWeight] = []
        for _, weight_record in weights_map.items():
            updated_weights.append(weight_record)
        profile_dict = profile.model_dump()
        profile_dict['weights'] = updated_weights
        profile_dict['preference_type'] = PreferenceType.LEARNED
        profile_dict['confidence'] = PreferenceConfidence.MEDIUM
        return PreferenceProfile(**profile_dict)

    def _determine_sources(self) -> List[str]:
        sources: List[str] = []
        if self.database_available:
            sources.append('database')
        if len(self._memory_profiles) > 0:
            sources.append('in_memory')
        return sources

    def _derive_recommendations(self, profile: PreferenceProfile) -> List[str]:
        recommendations: List[str] = []
        if profile.market_focus:
            recommendations.append('Prioritize market-aligned crop varieties')
        if profile.sustainability_focus:
            recommendations.append('Surface sustainability metrics in filtering results')
        if profile.risk_tolerance == RiskTolerance.LOW:
            recommendations.append('Filter out high-risk crop options')
        return recommendations

    def _detect_conflicts(self, profile: PreferenceProfile) -> List[str]:
        conflicts: List[str] = []
        for constraint in profile.constraints:
            if constraint.constraint_type == ConstraintType.EXCLUDE:
                for category in profile.crop_categories:
                    if self._terms_match(category, constraint.key):
                        message = (
                            f"Exclude constraint on '{constraint.key}' conflicts with preferred category '{category}'"
                        )
                        conflicts.append(message)
        if profile.management_style == ManagementStyle.HIGH_INTENSITY and profile.risk_tolerance == RiskTolerance.LOW:
            conflicts.append("High-intensity management with low risk tolerance may limit viable crops")
        return conflicts

    def _terms_match(self, candidate: str, target: str) -> bool:
        if CropFilteringAttributes is None:
            return candidate.strip().lower() == target.strip().lower()
        normalized_candidate = CropFilteringAttributes._normalize_term(candidate)  # type: ignore[attr-defined]
        normalized_target = CropFilteringAttributes._normalize_term(target)  # type: ignore[attr-defined]
        return normalized_candidate == normalized_target

    def _record_to_profile(self, record: Dict[str, Any]) -> PreferenceProfile:
        converted_weights: List[PreferenceWeight] = []
        weights_source = record.get('weights') or []
        for entry in weights_source:
            dimension_value = entry.get('dimension')
            key_value = entry.get('key')
            weight_value = entry.get('weight', 0.0)
            if dimension_value is None or key_value is None:
                continue
            try:
                dimension_enum = PreferenceDimension(dimension_value)
            except Exception:
                dimension_enum = PreferenceDimension.CUSTOM
            weight_instance = PreferenceWeight(
                dimension=dimension_enum,
                key=str(key_value),
                weight=float(weight_value)
            )
            converted_weights.append(weight_instance)
        constraints_source = record.get('constraints') or []
        converted_constraints: List[PreferenceConstraint] = []
        for entry in constraints_source:
            constraint_type = entry.get('constraint_type') or entry.get('type')
            dimension_value = entry.get('dimension') or PreferenceDimension.CUSTOM.value
            key_value = entry.get('key')
            if constraint_type is None or key_value is None:
                continue
            try:
                constraint_enum = ConstraintType(constraint_type)
            except Exception:
                constraint_enum = ConstraintType.REQUIRE
            try:
                dimension_enum = PreferenceDimension(dimension_value)
            except Exception:
                dimension_enum = PreferenceDimension.CUSTOM
            constraint_instance = PreferenceConstraint(
                constraint_type=constraint_enum,
                dimension=dimension_enum,
                key=str(key_value),
                limit_value=entry.get('limit_value'),
                notes=entry.get('notes')
            )
            converted_constraints.append(constraint_instance)
        preference_type_value = record.get('preference_type', PreferenceType.USER_DEFINED.value)
        try:
            preference_type_enum = PreferenceType(preference_type_value)
        except Exception:
            preference_type_enum = PreferenceType.USER_DEFINED
        confidence_value = record.get('confidence', PreferenceConfidence.MEDIUM.value)
        try:
            confidence_enum = PreferenceConfidence(confidence_value)
        except Exception:
            confidence_enum = PreferenceConfidence.MEDIUM
        management_value = record.get('management_style')
        management_enum = None
        if management_value:
            try:
                management_enum = ManagementStyle(management_value)
            except Exception:
                management_enum = None
        risk_value = record.get('risk_tolerance')
        risk_enum = None
        if risk_value:
            try:
                risk_enum = RiskTolerance(risk_value)
            except Exception:
                risk_enum = None
        profile_kwargs = {
            'preference_id': UUID(record['preference_id']) if record.get('preference_id') else None,
            'user_id': UUID(record['user_id']) if record.get('user_id') else None,
            'preference_type': preference_type_enum,
            'title': record.get('title'),
            'crop_categories': record.get('crop_categories') or [],
            'market_focus': record.get('market_focus') or [],
            'sustainability_focus': record.get('sustainability_focus') or [],
            'management_style': management_enum,
            'risk_tolerance': risk_enum,
            'weights': converted_weights,
            'constraints': converted_constraints,
            'priority_notes': record.get('priority_notes') or {},
            'metadata': record.get('profile_metadata') or record.get('metadata') or {},
            'confidence': confidence_enum,
            'created_at': self._parse_datetime(record.get('created_at')),
            'updated_at': self._parse_datetime(record.get('updated_at'))
        }
        return PreferenceProfile(**profile_kwargs)

    def _profile_to_record(self, profile: PreferenceProfile) -> Dict[str, Any]:
        record: Dict[str, Any] = {
            'preference_id': str(profile.preference_id) if profile.preference_id else None,
            'user_id': str(profile.user_id) if profile.user_id else None,
            'preference_type': profile.preference_type.value,
            'title': profile.title,
            'crop_categories': profile.crop_categories,
            'market_focus': profile.market_focus,
            'sustainability_focus': profile.sustainability_focus,
            'management_style': profile.management_style.value if profile.management_style else None,
            'risk_tolerance': profile.risk_tolerance.value if profile.risk_tolerance else None,
            'confidence': profile.confidence.value,
        }
        weights_value: List[Dict[str, Any]] = []
        for weight_record in profile.weights:
            weights_value.append({
                'dimension': weight_record.dimension.value,
                'key': weight_record.key,
                'weight': weight_record.weight
            })
        record['weights'] = weights_value
        constraints_value: List[Dict[str, Any]] = []
        for constraint in profile.constraints:
            constraints_value.append({
                'constraint_type': constraint.constraint_type.value,
                'dimension': constraint.dimension.value,
                'key': constraint.key,
                'limit_value': constraint.limit_value,
                'notes': constraint.notes
            })
        record['constraints'] = constraints_value
        return record

    def _memory_key(self, user_id: UUID, preference_type: Optional[str]) -> str:
        type_value = preference_type if preference_type else 'default'
        return f"{user_id}:{type_value}"

    def _weight_key(self, dimension: str, key: str) -> str:
        return f"{dimension}:{key}"

    def _resolve_dimension(self, context: Optional[Dict[str, Any]]) -> PreferenceDimension:
        if context is None:
            return PreferenceDimension.CUSTOM
        candidate_keys = ['dimension', 'preference_dimension', 'category']
        for key in candidate_keys:
            if key in context and context[key] is not None:
                value = str(context[key])
                try:
                    return PreferenceDimension(value)
                except Exception:
                    continue
        return PreferenceDimension.CUSTOM

    def _resolve_key(self, signal: PreferenceSignal, dimension: PreferenceDimension) -> str:
        context = signal.context or {}
        candidate_keys = ['key', 'preference_key', 'category', 'identifier']
        for key in candidate_keys:
            if key in context and context[key] is not None:
                return str(context[key])
        if dimension == PreferenceDimension.CROP_CATEGORY:
            return 'general_crop_interest'
        return 'general_preference'

    def _store_signal_history(self, user_id: UUID, signal: PreferenceSignal) -> None:
        key = str(user_id)
        if key not in self._signal_history:
            self._signal_history[key] = []
        entry = {
            'crop_id': str(signal.crop_id),
            'signal_type': signal.signal_type,
            'weight': signal.weight,
            'context': signal.context
        }
        self._signal_history[key].append(entry)

    def _parse_datetime(self, value: Optional[Any]) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except Exception:
            return None


crop_preference_service = CropPreferenceService()

__all__ = ['CropPreferenceService', 'crop_preference_service']
