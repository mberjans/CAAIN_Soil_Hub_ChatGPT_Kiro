"""
Operational constraint accommodation service for fertilizer timing.

This service evaluates operational constraints including equipment availability,
labor scheduling, field access conditions, and regulatory requirements. It
generates alternative schedules, resource allocation plans, and structured
constraints for downstream optimization services.
"""

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple

from models import (
    AlternativeScheduleOption,
    ConstraintStatus,
    OperationalConstraintReport,
    ResourceAllocationPlan,
    TimingConstraint,
    TimingConstraintType,
    TimingOptimizationRequest,
)

logger = logging.getLogger(__name__)


class OperationalConstraintService:
    """
    Evaluate and accommodate operational constraints for fertilizer timing.

    This service analyzes equipment availability, labor scheduling, field access
    conditions, and regulatory windows to identify constraints that affect
    fertilizer application timing. It generates alternative schedules when
    primary dates are blocked and produces resource allocation plans to support
    successful application execution.
    """

    def __init__(self) -> None:
        """Initialize the operational constraint service."""
        self._equipment_buffer_days = 3
        self._labor_buffer_days = 2
        self._field_access_moisture_threshold = 0.70
        self._field_access_critical_threshold = 0.80
        logger.info("OperationalConstraintService initialized")

    async def accommodate_constraints(
        self,
        request: TimingOptimizationRequest,
    ) -> OperationalConstraintReport:
        """
        Accommodate operational constraints and produce comprehensive report.

        This method evaluates all operational constraints affecting fertilizer
        timing decisions including equipment, labor, field access, and regulatory
        requirements. It generates alternative schedules when constraints block
        primary dates and creates resource allocation plans for viable timings.

        Args:
            request: Timing optimization request with field and resource details

        Returns:
            Comprehensive operational constraint report with status, alternatives,
            resource plans, and structured constraints
        """
        logger.info(
            "Accommodating operational constraints for request %s",
            request.request_id,
        )

        constraint_status: List[ConstraintStatus] = []
        generated_constraints: List[TimingConstraint] = []

        equipment_statuses = self._evaluate_equipment_constraints(request)
        constraint_status.extend(equipment_statuses)

        labor_statuses = self._evaluate_labor_constraints(request)
        constraint_status.extend(labor_statuses)

        field_access_statuses = self._evaluate_field_access(request)
        constraint_status.extend(field_access_statuses)

        regulatory_notes = self._evaluate_regulatory_windows(request)

        self._populate_generated_constraints(
            generated_constraints,
            constraint_status,
            request,
        )

        alternative_options = self._generate_alternative_schedules(
            request,
            constraint_status,
        )

        resource_plans = self._create_resource_allocation_plans(
            request,
            constraint_status,
        )

        summary = self._build_constraint_summary(
            request,
            constraint_status,
            alternative_options,
            resource_plans,
        )

        metadata: Dict[str, str] = {}
        metadata["field_id"] = request.field_id
        metadata["crop_type"] = request.crop_type
        metadata["optimization_horizon_days"] = str(request.optimization_horizon_days)

        report = OperationalConstraintReport(
            request_id=request.request_id,
            generated_at=datetime.now(timezone.utc),
            constraint_status=constraint_status,
            alternative_options=alternative_options,
            resource_plans=resource_plans,
            regulatory_notes=regulatory_notes,
            generated_constraints=generated_constraints,
            summary=summary,
            metadata=metadata,
        )

        logger.info(
            "Constraint accommodation complete for request %s with %d constraints",
            request.request_id,
            len(constraint_status),
        )

        return report

    def _evaluate_equipment_constraints(
        self,
        request: TimingOptimizationRequest,
    ) -> List[ConstraintStatus]:
        """
        Evaluate equipment availability constraints.

        Equipment constraints assess whether necessary application equipment is
        available during optimal timing windows. Constraints consider equipment
        type, capacity, and scheduled maintenance or prior commitments.

        Args:
            request: Timing optimization request with equipment availability

        Returns:
            List of constraint status records for equipment availability
        """
        statuses: List[ConstraintStatus] = []
        equipment_availability = request.equipment_availability or {}

        if not equipment_availability:
            blocking_status = ConstraintStatus(
                constraint_type=TimingConstraintType.EQUIPMENT_AVAILABILITY,
                name="Equipment Availability - No Equipment Scheduled",
                severity=0.9,
                blocking=True,
                impacted_timings=[],
                notes=["No equipment availability data provided for this field."],
                recommendations=[
                    "Schedule equipment for application windows.",
                    "Confirm equipment reservations with operations team.",
                ],
            )
            statuses.append(blocking_status)
            logger.debug("No equipment availability data provided")
            return statuses

        total_equipment_types = len(equipment_availability)
        available_dates_count = 0

        for equipment_type, date_strings in equipment_availability.items():
            available_dates_count += len(date_strings)

        logger.debug(
            "Evaluating %d equipment types with %d total available dates",
            total_equipment_types,
            available_dates_count,
        )

        if available_dates_count < 2:
            severity = 0.8
            blocking = True
            notes: List[str] = []
            notes.append(
                "Limited equipment availability may restrict timing flexibility."
            )
            recommendations: List[str] = []
            recommendations.append(
                "Coordinate with neighboring operations to share equipment."
            )
            recommendations.append(
                "Reserve backup equipment for weather-related delays."
            )

            status = ConstraintStatus(
                constraint_type=TimingConstraintType.EQUIPMENT_AVAILABILITY,
                name="Equipment Availability - Limited Dates",
                severity=severity,
                blocking=blocking,
                impacted_timings=[],
                notes=notes,
                recommendations=recommendations,
            )
            statuses.append(status)
        else:
            severity = 0.3
            blocking = False
            notes_adequate: List[str] = []
            notes_adequate.append(
                f"Equipment available on {available_dates_count} dates across {total_equipment_types} types."
            )
            recommendations_adequate: List[str] = []
            recommendations_adequate.append(
                "Confirm equipment capacity matches field acreage requirements."
            )

            status = ConstraintStatus(
                constraint_type=TimingConstraintType.EQUIPMENT_AVAILABILITY,
                name="Equipment Availability - Adequate",
                severity=severity,
                blocking=blocking,
                impacted_timings=[],
                notes=notes_adequate,
                recommendations=recommendations_adequate,
            )
            statuses.append(status)

        return statuses

    def _evaluate_labor_constraints(
        self,
        request: TimingOptimizationRequest,
    ) -> List[ConstraintStatus]:
        """
        Evaluate labor availability constraints.

        Labor constraints assess whether sufficient skilled labor is available
        during application windows. This includes operator skill requirements,
        peak season conflicts, and backup labor availability.

        Args:
            request: Timing optimization request with labor availability

        Returns:
            List of constraint status records for labor availability
        """
        statuses: List[ConstraintStatus] = []
        labor_availability = request.labor_availability or {}

        if not labor_availability:
            blocking_status = ConstraintStatus(
                constraint_type=TimingConstraintType.LABOR_AVAILABILITY,
                name="Labor Availability - No Labor Scheduled",
                severity=0.85,
                blocking=True,
                impacted_timings=[],
                notes=["No labor availability data provided for this field."],
                recommendations=[
                    "Schedule operators for application windows.",
                    "Ensure certified applicators are available for regulated products.",
                ],
            )
            statuses.append(blocking_status)
            logger.debug("No labor availability data provided")
            return statuses

        total_worker_days = 0
        dates_with_labor = 0

        for labor_date_str, worker_count in labor_availability.items():
            dates_with_labor += 1
            total_worker_days += worker_count

        logger.debug(
            "Evaluating labor availability: %d dates with %d total worker-days",
            dates_with_labor,
            total_worker_days,
        )

        if total_worker_days < 3:
            severity = 0.75
            blocking = True
            notes: List[str] = []
            notes.append(
                "Insufficient labor availability may delay application timing."
            )
            recommendations: List[str] = []
            recommendations.append(
                "Arrange additional labor for peak application periods."
            )
            recommendations.append(
                "Cross-train operators to provide scheduling flexibility."
            )

            status = ConstraintStatus(
                constraint_type=TimingConstraintType.LABOR_AVAILABILITY,
                name="Labor Availability - Insufficient",
                severity=severity,
                blocking=blocking,
                impacted_timings=[],
                notes=notes,
                recommendations=recommendations,
            )
            statuses.append(status)
        else:
            severity = 0.25
            blocking = False
            notes_adequate: List[str] = []
            notes_adequate.append(
                f"Labor available on {dates_with_labor} dates with {total_worker_days} worker-days."
            )
            recommendations_adequate: List[str] = []
            recommendations_adequate.append(
                "Verify operator certifications for regulated fertilizer products."
            )

            status = ConstraintStatus(
                constraint_type=TimingConstraintType.LABOR_AVAILABILITY,
                name="Labor Availability - Adequate",
                severity=severity,
                blocking=blocking,
                impacted_timings=[],
                notes=notes_adequate,
                recommendations=recommendations_adequate,
            )
            statuses.append(status)

        return statuses

    def _evaluate_field_access(
        self,
        request: TimingOptimizationRequest,
    ) -> List[ConstraintStatus]:
        """
        Evaluate field access constraints based on soil and field conditions.

        Field access constraints evaluate whether field conditions support heavy
        equipment traffic without excessive soil compaction or rutting. This
        includes soil moisture, drainage, texture, and trafficability assessment.

        Args:
            request: Timing optimization request with field characteristics

        Returns:
            List of constraint status records for field access
        """
        statuses: List[ConstraintStatus] = []
        moisture = request.soil_moisture_capacity
        soil_type = request.soil_type or ""
        drainage_class = request.drainage_class or ""

        logger.debug(
            "Evaluating field access: moisture=%.2f, soil=%s, drainage=%s",
            moisture,
            soil_type,
            drainage_class,
        )

        soil_type_lower = soil_type.lower()
        drainage_lower = drainage_class.lower()

        base_severity = 0.2
        severity_adjustment = 0.0

        if moisture >= self._field_access_critical_threshold:
            severity_adjustment += 0.6
        elif moisture >= self._field_access_moisture_threshold:
            severity_adjustment += 0.3

        if "clay" in soil_type_lower:
            severity_adjustment += 0.2

        if "poor" in drainage_lower:
            severity_adjustment += 0.25

        severity = base_severity + severity_adjustment
        if severity > 1.0:
            severity = 1.0

        blocking = severity >= 0.7

        notes: List[str] = []
        recommendations: List[str] = []

        if moisture >= self._field_access_critical_threshold:
            notes.append(
                "Soil moisture near saturation increases rutting and compaction risk."
            )
            recommendations.append(
                "Delay application until soil moisture drops below 70%."
            )
            recommendations.append(
                "Use low ground pressure equipment if application cannot be delayed."
            )
        elif moisture >= self._field_access_moisture_threshold:
            notes.append(
                "Elevated soil moisture requires careful equipment selection."
            )
            recommendations.append(
                "Monitor field conditions daily before mobilizing equipment."
            )

        if "clay" in soil_type_lower:
            notes.append(
                "Clay soils are particularly vulnerable to compaction when wet."
            )
            recommendations.append(
                "Reduce tire pressure or use tracked equipment on clay soils."
            )

        if "poor" in drainage_lower:
            notes.append(
                "Poor drainage extends the time required for fields to become trafficable."
            )
            recommendations.append(
                "Plan for extended drying periods after rainfall events."
            )

        if not notes:
            notes.append("Field access conditions are favorable for equipment traffic.")

        if not recommendations:
            recommendations.append(
                "Continue monitoring soil moisture before application."
            )

        status = ConstraintStatus(
            constraint_type=TimingConstraintType.SOIL_CONDITIONS,
            name="Field Access - Trafficability",
            severity=severity,
            blocking=blocking,
            impacted_timings=[],
            notes=notes,
            recommendations=recommendations,
        )
        statuses.append(status)

        return statuses

    def _evaluate_regulatory_windows(
        self,
        request: TimingOptimizationRequest,
    ) -> List[str]:
        """
        Evaluate regulatory compliance requirements for fertilizer application.

        Regulatory constraints include setback distances from water bodies,
        buffer zone requirements, seasonal application restrictions, and
        weather-based prohibitions such as frozen ground or imminent rainfall.

        Args:
            request: Timing optimization request with field location

        Returns:
            List of regulatory notes and compliance observations
        """
        notes: List[str] = []

        notes.append(
            "Maintain required setback distances from water bodies and wetlands."
        )
        notes.append(
            "Avoid applications when soil is frozen or snow-covered in regulated watersheds."
        )
        notes.append(
            "Check state and local regulations for seasonal application restrictions."
        )

        crop_type = request.crop_type or ""
        crop_type_lower = crop_type.lower()

        if "corn" in crop_type_lower:
            notes.append(
                "For corn, follow 4R nutrient stewardship guidelines for nitrogen timing."
            )

        logger.debug("Generated %d regulatory notes", len(notes))

        return notes

    def _generate_alternative_schedules(
        self,
        request: TimingOptimizationRequest,
        constraint_status: List[ConstraintStatus],
    ) -> List[AlternativeScheduleOption]:
        """
        Generate alternative schedules when primary dates are blocked by constraints.

        Alternative schedules identify backup application dates that avoid or
        minimize constraint conflicts. Alternatives consider equipment and labor
        availability, field access windows, and regulatory compliance.

        Args:
            request: Timing optimization request with timing preferences
            constraint_status: Evaluated constraint status records

        Returns:
            List of alternative schedule options with suitability scores
        """
        alternatives: List[AlternativeScheduleOption] = []

        has_blocking_constraint = False
        index = 0
        count = len(constraint_status)
        while index < count:
            status = constraint_status[index]
            if status.blocking:
                has_blocking_constraint = True
                break
            index += 1

        if not has_blocking_constraint:
            logger.debug("No blocking constraints; no alternatives generated")
            return alternatives

        logger.debug("Generating alternative schedules due to blocking constraints")

        primary_date = self._estimate_primary_application_date(request)
        alternative_date = primary_date + timedelta(days=7)

        fertilizer_types: List[str] = []
        for fertilizer_type in request.fertilizer_requirements.keys():
            fertilizer_types.append(fertilizer_type)

        for fertilizer_type in fertilizer_types:
            suitability_score = 0.65

            reason = "Alternative date to avoid equipment and labor constraints."

            option = AlternativeScheduleOption(
                fertilizer_type=fertilizer_type,
                primary_date=primary_date,
                alternative_date=alternative_date,
                reason=reason,
                suitability_score=suitability_score,
            )
            alternatives.append(option)

        logger.debug("Generated %d alternative schedule options", len(alternatives))

        return alternatives

    def _create_resource_allocation_plans(
        self,
        request: TimingOptimizationRequest,
        constraint_status: List[ConstraintStatus],
    ) -> List[ResourceAllocationPlan]:
        """
        Create resource allocation plans aligned with constraint accommodation.

        Resource allocation plans specify equipment assignments, labor
        requirements, and readiness actions needed to execute fertilizer
        applications on approved dates. Plans identify gaps between required
        and available resources.

        Args:
            request: Timing optimization request with resource availability
            constraint_status: Evaluated constraint status records

        Returns:
            List of resource allocation plans for viable application dates
        """
        plans: List[ResourceAllocationPlan] = []

        equipment_availability = request.equipment_availability or {}
        labor_availability = request.labor_availability or {}

        available_dates: Set[date] = set()

        for equipment_type, date_strings in equipment_availability.items():
            for date_str in date_strings:
                parsed_date = self._parse_date_string(date_str)
                if parsed_date is not None:
                    available_dates.add(parsed_date)

        for labor_date_str in labor_availability.keys():
            parsed_date = self._parse_date_string(labor_date_str)
            if parsed_date is not None:
                available_dates.add(parsed_date)

        if not available_dates:
            logger.debug("No resource availability dates found")
            return plans

        sorted_dates: List[date] = []
        for available_date in available_dates:
            sorted_dates.append(available_date)
        sorted_dates.sort()

        limit = min(3, len(sorted_dates))
        index = 0
        while index < limit:
            plan_date = sorted_dates[index]

            equipment_assignments: List[str] = []
            for equipment_type, date_strings in equipment_availability.items():
                date_str = plan_date.isoformat()
                if date_str in date_strings:
                    equipment_assignments.append(equipment_type)

            labor_required = 2
            labor_available = labor_availability.get(plan_date.isoformat(), 0)

            readiness_actions: List[str] = []
            if labor_available < labor_required:
                gap = labor_required - labor_available
                readiness_actions.append(
                    f"Arrange {gap} additional operator(s) for {plan_date.isoformat()}."
                )

            if not equipment_assignments:
                readiness_actions.append(
                    f"Reserve equipment for application on {plan_date.isoformat()}."
                )

            plan = ResourceAllocationPlan(
                plan_date=plan_date,
                equipment=equipment_assignments,
                labor_required=labor_required,
                labor_available=labor_available,
                readiness_actions=readiness_actions,
            )
            plans.append(plan)
            index += 1

        logger.debug("Created %d resource allocation plans", len(plans))

        return plans

    def _populate_generated_constraints(
        self,
        generated_constraints: List[TimingConstraint],
        constraint_status: List[ConstraintStatus],
        request: TimingOptimizationRequest,
    ) -> None:
        """
        Populate structured TimingConstraint objects for downstream optimizers.

        Generated constraints convert ConstraintStatus records into standardized
        TimingConstraint objects that downstream optimization services can
        consume directly.

        Args:
            generated_constraints: List to populate with generated constraints
            constraint_status: Evaluated constraint status records
            request: Timing optimization request for context
        """
        index = 0
        count = len(constraint_status)
        while index < count:
            status = constraint_status[index]

            description = status.name
            if status.notes:
                first_note = status.notes[0]
                description = f"{description}: {first_note}"

            constraint = TimingConstraint(
                constraint_type=status.constraint_type,
                description=description,
                severity=status.severity,
            )
            generated_constraints.append(constraint)
            index += 1

        logger.debug(
            "Generated %d structured constraints for downstream optimizers",
            len(generated_constraints),
        )

    def _build_constraint_summary(
        self,
        request: TimingOptimizationRequest,
        constraint_status: List[ConstraintStatus],
        alternative_options: List[AlternativeScheduleOption],
        resource_plans: List[ResourceAllocationPlan],
    ) -> str:
        """
        Build narrative summary describing key constraint findings.

        The summary provides a human-readable overview of constraint evaluation
        results, highlighting blocking constraints, resource gaps, and
        recommended actions.

        Args:
            request: Timing optimization request for context
            constraint_status: Evaluated constraint status records
            alternative_options: Generated alternative schedule options
            resource_plans: Created resource allocation plans

        Returns:
            Narrative summary of constraint accommodation findings
        """
        parts: List[str] = []

        parts.append(
            f"Operational constraint evaluation for field {request.field_id} ({request.crop_type})."
        )

        blocking_count = 0
        non_blocking_count = 0

        index = 0
        count = len(constraint_status)
        while index < count:
            status = constraint_status[index]
            if status.blocking:
                blocking_count += 1
            else:
                non_blocking_count += 1
            index += 1

        parts.append(
            f"Identified {len(constraint_status)} constraints: {blocking_count} blocking, {non_blocking_count} non-blocking."
        )

        if blocking_count > 0:
            parts.append(
                f"Generated {len(alternative_options)} alternative schedule options to accommodate blocking constraints."
            )

        parts.append(
            f"Created {len(resource_plans)} resource allocation plans for viable application dates."
        )

        if resource_plans:
            parts.append(
                "Review resource plans to identify equipment and labor gaps requiring coordination."
            )

        summary = " ".join(parts)
        return summary

    def _estimate_primary_application_date(
        self,
        request: TimingOptimizationRequest,
    ) -> date:
        """
        Estimate primary application date based on planting date and crop type.

        Args:
            request: Timing optimization request with planting date

        Returns:
            Estimated primary application date
        """
        planting_date = request.planting_date
        offset_days = 30
        primary_date = planting_date + timedelta(days=offset_days)
        return primary_date

    def _parse_date_string(
        self,
        date_str: str,
    ) -> Optional[date]:
        """
        Parse date string in ISO format.

        Args:
            date_str: Date string to parse

        Returns:
            Parsed date or None if parsing fails
        """
        try:
            parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
            return parsed
        except ValueError:
            logger.debug("Unable to parse date string: %s", date_str)
            return None


__all__ = ["OperationalConstraintService"]
