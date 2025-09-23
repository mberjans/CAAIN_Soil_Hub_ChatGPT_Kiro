"""
Context Management System for AFAS AI Agent

Manages conversation context, agricultural context, and user session state
for enhanced AI interactions with memory and continuity.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)


class ContextType(str, Enum):
    """Types of context that can be managed."""
    CONVERSATION = "conversation"
    AGRICULTURAL = "agricultural"
    USER_PROFILE = "user_profile"
    SESSION = "session"
    FARM_DATA = "farm_data"
    RECOMMENDATION_HISTORY = "recommendation_history"


class ContextPriority(str, Enum):
    """Priority levels for context information."""
    CRITICAL = "critical"      # Essential for accurate responses
    HIGH = "high"             # Important for quality responses
    MEDIUM = "medium"         # Helpful for better responses
    LOW = "low"              # Nice to have for personalization


class ContextScope(str, Enum):
    """Scope of context information."""
    GLOBAL = "global"         # Available across all sessions
    SESSION = "session"       # Available within current session
    CONVERSATION = "conversation"  # Available within current conversation
    TEMPORARY = "temporary"   # Short-lived context


class ContextEntry(BaseModel):
    """Individual context entry with metadata."""
    
    id: str = Field(..., description="Unique identifier for context entry")
    context_type: ContextType = Field(..., description="Type of context")
    priority: ContextPriority = Field(default=ContextPriority.MEDIUM)
    scope: ContextScope = Field(default=ContextScope.SESSION)
    
    # Content
    data: Dict[str, Any] = Field(..., description="Context data")
    summary: Optional[str] = Field(None, description="Human-readable summary")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Expiration time")
    access_count: int = Field(default=0, description="Number of times accessed")
    last_accessed: Optional[datetime] = Field(None, description="Last access time")
    
    # Relationships
    related_entries: List[str] = Field(default_factory=list, description="Related context IDs")
    source: Optional[str] = Field(None, description="Source of context information")
    
    @validator('expires_at', pre=True, always=True)
    def set_default_expiration(cls, v, values):
        """Set default expiration based on scope if not provided."""
        if v is None:
            scope = values.get('scope')
            now = datetime.utcnow()
            
            if scope == ContextScope.TEMPORARY:
                return now + timedelta(hours=1)
            elif scope == ContextScope.CONVERSATION:
                return now + timedelta(hours=24)
            elif scope == ContextScope.SESSION:
                return now + timedelta(days=7)
            else:  # GLOBAL
                return now + timedelta(days=30)
        return v
    
    def is_expired(self) -> bool:
        """Check if context entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def access(self):
        """Record access to this context entry."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()


class ConversationContext(BaseModel):
    """Enhanced conversation context with agricultural awareness."""
    
    user_id: str
    session_id: str
    conversation_id: str
    
    # Conversation state
    messages: List[Dict[str, str]] = Field(default_factory=list)
    current_topic: Optional[str] = Field(None, description="Current conversation topic")
    question_sequence: List[str] = Field(default_factory=list, description="Sequence of question types")
    
    # Agricultural context
    farm_profile: Optional[Dict[str, Any]] = Field(None, description="Farm profile information")
    current_crop_season: Optional[str] = Field(None, description="Current crop season context")
    active_recommendations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # User preferences
    communication_style: Optional[str] = Field(None, description="Preferred communication style")
    expertise_level: Optional[str] = Field(None, description="User's agricultural expertise level")
    preferred_units: Optional[str] = Field(None, description="Preferred measurement units")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    total_interactions: int = Field(default=0)
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to the conversation."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        
        self.messages.append(message)
        self.total_interactions += 1
        self.last_updated = datetime.utcnow()
    
    def get_recent_messages(self, count: int = 10) -> List[Dict[str, str]]:
        """Get recent messages from conversation."""
        return self.messages[-count:] if self.messages else []
    
    def get_context_summary(self) -> str:
        """Generate a summary of the conversation context."""
        if not self.messages:
            return "New conversation"
        
        recent_topics = []
        if self.current_topic:
            recent_topics.append(self.current_topic)
        
        if self.question_sequence:
            recent_topics.extend(self.question_sequence[-3:])
        
        summary_parts = []
        if recent_topics:
            summary_parts.append(f"Recent topics: {', '.join(recent_topics)}")
        
        if self.farm_profile:
            farm_info = []
            if self.farm_profile.get('location'):
                farm_info.append(f"Location: {self.farm_profile['location']}")
            if self.farm_profile.get('farm_size_acres'):
                farm_info.append(f"Size: {self.farm_profile['farm_size_acres']} acres")
            if self.farm_profile.get('primary_crops'):
                farm_info.append(f"Crops: {', '.join(self.farm_profile['primary_crops'])}")
            
            if farm_info:
                summary_parts.append(f"Farm: {'; '.join(farm_info)}")
        
        if self.active_recommendations:
            summary_parts.append(f"Active recommendations: {len(self.active_recommendations)}")
        
        return " | ".join(summary_parts) if summary_parts else "General conversation"


class ContextManager:
    """
    Comprehensive context management system for AI agent interactions.
    
    Manages conversation context, agricultural context, user profiles,
    and session state with intelligent retrieval and persistence.
    """
    
    def __init__(self, 
                 max_contexts_per_user: int = 1000,
                 cleanup_interval_hours: int = 6,
                 enable_persistence: bool = True):
        """
        Initialize context manager.
        
        Args:
            max_contexts_per_user: Maximum context entries per user
            cleanup_interval_hours: Hours between cleanup operations
            enable_persistence: Whether to enable context persistence
        """
        self.max_contexts_per_user = max_contexts_per_user
        self.cleanup_interval_hours = cleanup_interval_hours
        self.enable_persistence = enable_persistence
        
        # In-memory storage
        self.contexts: Dict[str, Dict[str, ContextEntry]] = {}  # user_id -> {context_id -> entry}
        self.conversations: Dict[str, ConversationContext] = {}  # conversation_key -> context
        self.user_sessions: Dict[str, Dict[str, Any]] = {}  # user_id -> session_data
        
        # Indexes for efficient retrieval
        self.context_by_type: Dict[ContextType, List[str]] = {ct: [] for ct in ContextType}
        self.context_by_tags: Dict[str, List[str]] = {}
        
        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        
        logger.info("Context manager initialized")
    
    async def start(self):
        """Start the context manager and background tasks."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
        logger.info("Context manager started")
    
    async def stop(self):
        """Stop the context manager and cleanup tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
        logger.info("Context manager stopped")
    
    def _generate_context_id(self, user_id: str, context_type: ContextType, 
                           additional_data: Optional[str] = None) -> str:
        """Generate unique context ID."""
        base_string = f"{user_id}:{context_type}:{datetime.utcnow().isoformat()}"
        if additional_data:
            base_string += f":{additional_data}"
        
        return hashlib.md5(base_string.encode()).hexdigest()[:16]
    
    def _generate_conversation_key(self, user_id: str, session_id: str) -> str:
        """Generate conversation key."""
        return f"{user_id}:{session_id}"
    
    async def store_context(self, 
                          user_id: str,
                          context_type: ContextType,
                          data: Dict[str, Any],
                          priority: ContextPriority = ContextPriority.MEDIUM,
                          scope: ContextScope = ContextScope.SESSION,
                          summary: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          source: Optional[str] = None,
                          expires_at: Optional[datetime] = None) -> str:
        """
        Store context information.
        
        Args:
            user_id: User identifier
            context_type: Type of context
            data: Context data
            priority: Priority level
            scope: Context scope
            summary: Human-readable summary
            tags: Searchable tags
            source: Source of information
            expires_at: Custom expiration time
            
        Returns:
            Context entry ID
        """
        try:
            # Generate context ID
            context_id = self._generate_context_id(user_id, context_type, 
                                                 json.dumps(data, sort_keys=True)[:50])
            
            # Create context entry
            entry = ContextEntry(
                id=context_id,
                context_type=context_type,
                priority=priority,
                scope=scope,
                data=data,
                summary=summary or f"{context_type} context for {user_id}",
                tags=tags or [],
                source=source,
                expires_at=expires_at
            )
            
            # Store in user's context collection
            if user_id not in self.contexts:
                self.contexts[user_id] = {}
            
            self.contexts[user_id][context_id] = entry
            
            # Update indexes
            self.context_by_type[context_type].append(context_id)
            
            for tag in entry.tags:
                if tag not in self.context_by_tags:
                    self.context_by_tags[tag] = []
                self.context_by_tags[tag].append(context_id)
            
            # Enforce user context limits
            await self._enforce_user_context_limits(user_id)
            
            logger.debug(f"Stored context {context_id} for user {user_id}")
            return context_id
            
        except Exception as e:
            logger.error(f"Failed to store context for user {user_id}: {e}")
            raise
    
    async def get_context(self, user_id: str, context_id: str) -> Optional[ContextEntry]:
        """
        Retrieve specific context entry.
        
        Args:
            user_id: User identifier
            context_id: Context entry ID
            
        Returns:
            Context entry if found and not expired
        """
        try:
            if user_id not in self.contexts:
                return None
            
            entry = self.contexts[user_id].get(context_id)
            if not entry:
                return None
            
            if entry.is_expired():
                await self._remove_context(user_id, context_id)
                return None
            
            # Record access
            entry.access()
            
            return entry
            
        except Exception as e:
            logger.error(f"Failed to get context {context_id} for user {user_id}: {e}")
            return None
    
    async def get_contexts_by_type(self, 
                                 user_id: str, 
                                 context_type: ContextType,
                                 limit: int = 10) -> List[ContextEntry]:
        """
        Get contexts by type for a user.
        
        Args:
            user_id: User identifier
            context_type: Type of context to retrieve
            limit: Maximum number of contexts to return
            
        Returns:
            List of context entries
        """
        try:
            if user_id not in self.contexts:
                return []
            
            user_contexts = self.contexts[user_id]
            matching_contexts = []
            
            for entry in user_contexts.values():
                if entry.context_type == context_type and not entry.is_expired():
                    entry.access()
                    matching_contexts.append(entry)
            
            # Sort by priority and recency
            matching_contexts.sort(
                key=lambda x: (x.priority.value, x.updated_at),
                reverse=True
            )
            
            return matching_contexts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get contexts by type for user {user_id}: {e}")
            return []
    
    async def search_contexts(self, 
                            user_id: str,
                            query: Optional[str] = None,
                            tags: Optional[List[str]] = None,
                            context_types: Optional[List[ContextType]] = None,
                            priority_min: Optional[ContextPriority] = None,
                            limit: int = 20) -> List[ContextEntry]:
        """
        Search contexts with various filters.
        
        Args:
            user_id: User identifier
            query: Text query to search in summaries and data
            tags: Tags to filter by
            context_types: Context types to filter by
            priority_min: Minimum priority level
            limit: Maximum results to return
            
        Returns:
            List of matching context entries
        """
        try:
            if user_id not in self.contexts:
                return []
            
            user_contexts = self.contexts[user_id]
            matching_contexts = []
            
            for entry in user_contexts.values():
                if entry.is_expired():
                    continue
                
                # Filter by context type
                if context_types and entry.context_type not in context_types:
                    continue
                
                # Filter by priority
                if priority_min and entry.priority.value < priority_min.value:
                    continue
                
                # Filter by tags
                if tags and not any(tag in entry.tags for tag in tags):
                    continue
                
                # Text search in summary and data
                if query:
                    search_text = (entry.summary or "").lower()
                    search_text += " " + json.dumps(entry.data).lower()
                    
                    if query.lower() not in search_text:
                        continue
                
                entry.access()
                matching_contexts.append(entry)
            
            # Sort by relevance (priority, access count, recency)
            matching_contexts.sort(
                key=lambda x: (x.priority.value, x.access_count, x.updated_at),
                reverse=True
            )
            
            return matching_contexts[:limit]
            
        except Exception as e:
            logger.error(f"Failed to search contexts for user {user_id}: {e}")
            return []
    
    async def get_conversation_context(self, 
                                    user_id: str, 
                                    session_id: str) -> ConversationContext:
        """
        Get or create conversation context.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            
        Returns:
            Conversation context
        """
        try:
            conversation_key = self._generate_conversation_key(user_id, session_id)
            
            if conversation_key not in self.conversations:
                # Create new conversation context
                conversation_id = self._generate_context_id(user_id, ContextType.CONVERSATION, session_id)
                
                self.conversations[conversation_key] = ConversationContext(
                    user_id=user_id,
                    session_id=session_id,
                    conversation_id=conversation_id
                )
                
                logger.debug(f"Created new conversation context for {conversation_key}")
            
            return self.conversations[conversation_key]
            
        except Exception as e:
            logger.error(f"Failed to get conversation context for {user_id}:{session_id}: {e}")
            # Return minimal context on error
            return ConversationContext(
                user_id=user_id,
                session_id=session_id,
                conversation_id="error"
            )
    
    async def update_conversation_context(self,
                                        user_id: str,
                                        session_id: str,
                                        **updates) -> bool:
        """
        Update conversation context with new information.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            **updates: Fields to update
            
        Returns:
            Success status
        """
        try:
            context = await self.get_conversation_context(user_id, session_id)
            
            for field, value in updates.items():
                if hasattr(context, field):
                    setattr(context, field, value)
            
            context.last_updated = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update conversation context: {e}")
            return False
    
    async def get_relevant_context(self,
                                 user_id: str,
                                 session_id: str,
                                 query: Optional[str] = None,
                                 context_types: Optional[List[ContextType]] = None,
                                 max_contexts: int = 10) -> Dict[str, Any]:
        """
        Get relevant context for generating responses.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            query: Current query/message
            context_types: Specific context types to include
            max_contexts: Maximum contexts to return
            
        Returns:
            Structured context information
        """
        try:
            # Get conversation context
            conversation = await self.get_conversation_context(user_id, session_id)
            
            # Search for relevant contexts
            search_tags = []
            if query:
                # Extract potential tags from query
                query_words = query.lower().split()
                agricultural_terms = ['soil', 'crop', 'fertilizer', 'plant', 'farm', 'field', 
                                    'nitrogen', 'phosphorus', 'potassium', 'ph', 'organic']
                search_tags = [word for word in query_words if word in agricultural_terms]
            
            relevant_contexts = await self.search_contexts(
                user_id=user_id,
                query=query,
                tags=search_tags,
                context_types=context_types,
                limit=max_contexts
            )
            
            # Structure the context
            structured_context = {
                "conversation": {
                    "summary": conversation.get_context_summary(),
                    "recent_messages": conversation.get_recent_messages(5),
                    "current_topic": conversation.current_topic,
                    "question_sequence": conversation.question_sequence[-5:],
                    "total_interactions": conversation.total_interactions
                },
                "agricultural": {
                    "farm_profile": conversation.farm_profile,
                    "current_season": conversation.current_crop_season,
                    "active_recommendations": conversation.active_recommendations
                },
                "user_preferences": {
                    "communication_style": conversation.communication_style,
                    "expertise_level": conversation.expertise_level,
                    "preferred_units": conversation.preferred_units
                },
                "relevant_contexts": []
            }
            
            # Add relevant contexts by type
            for entry in relevant_contexts:
                context_info = {
                    "id": entry.id,
                    "type": entry.context_type,
                    "priority": entry.priority,
                    "summary": entry.summary,
                    "data": entry.data,
                    "tags": entry.tags,
                    "created_at": entry.created_at.isoformat(),
                    "access_count": entry.access_count
                }
                structured_context["relevant_contexts"].append(context_info)
            
            return structured_context
            
        except Exception as e:
            logger.error(f"Failed to get relevant context: {e}")
            return {"error": str(e)}
    
    async def store_agricultural_context(self,
                                       user_id: str,
                                       farm_data: Dict[str, Any],
                                       source: str = "user_input") -> str:
        """
        Store agricultural context information.
        
        Args:
            user_id: User identifier
            farm_data: Farm and agricultural data
            source: Source of the data
            
        Returns:
            Context ID
        """
        # Extract tags from farm data
        tags = ["agricultural", "farm_data"]
        
        if farm_data.get('location'):
            tags.append("location")
        if farm_data.get('soil_data'):
            tags.extend(["soil", "soil_test"])
        if farm_data.get('crops'):
            tags.extend(["crops", "crop_selection"])
        if farm_data.get('equipment'):
            tags.append("equipment")
        
        # Generate summary
        summary_parts = []
        if farm_data.get('farm_size_acres'):
            summary_parts.append(f"{farm_data['farm_size_acres']} acre farm")
        if farm_data.get('location'):
            summary_parts.append(f"in {farm_data['location']}")
        if farm_data.get('primary_crops'):
            summary_parts.append(f"growing {', '.join(farm_data['primary_crops'])}")
        
        summary = "Farm profile: " + "; ".join(summary_parts) if summary_parts else "Farm data"
        
        return await self.store_context(
            user_id=user_id,
            context_type=ContextType.AGRICULTURAL,
            data=farm_data,
            priority=ContextPriority.HIGH,
            scope=ContextScope.GLOBAL,
            summary=summary,
            tags=tags,
            source=source
        )
    
    async def store_recommendation_context(self,
                                         user_id: str,
                                         recommendation: Dict[str, Any],
                                         question_type: str) -> str:
        """
        Store recommendation context for future reference.
        
        Args:
            user_id: User identifier
            recommendation: Recommendation data
            question_type: Type of question that generated the recommendation
            
        Returns:
            Context ID
        """
        tags = ["recommendation", question_type.lower()]
        
        # Add specific tags based on recommendation content
        if "crop" in recommendation.get("content", "").lower():
            tags.append("crop_recommendation")
        if "fertilizer" in recommendation.get("content", "").lower():
            tags.append("fertilizer_recommendation")
        if "soil" in recommendation.get("content", "").lower():
            tags.append("soil_recommendation")
        
        summary = f"{question_type} recommendation: {recommendation.get('summary', 'Agricultural advice')}"
        
        return await self.store_context(
            user_id=user_id,
            context_type=ContextType.RECOMMENDATION_HISTORY,
            data=recommendation,
            priority=ContextPriority.HIGH,
            scope=ContextScope.GLOBAL,
            summary=summary,
            tags=tags,
            source="afas_recommendation_engine"
        )
    
    async def _remove_context(self, user_id: str, context_id: str):
        """Remove context entry and update indexes."""
        if user_id in self.contexts and context_id in self.contexts[user_id]:
            entry = self.contexts[user_id][context_id]
            
            # Remove from type index
            if context_id in self.context_by_type[entry.context_type]:
                self.context_by_type[entry.context_type].remove(context_id)
            
            # Remove from tag indexes
            for tag in entry.tags:
                if tag in self.context_by_tags and context_id in self.context_by_tags[tag]:
                    self.context_by_tags[tag].remove(context_id)
            
            # Remove the entry
            del self.contexts[user_id][context_id]
    
    async def _enforce_user_context_limits(self, user_id: str):
        """Enforce maximum context limits per user."""
        if user_id not in self.contexts:
            return
        
        user_contexts = self.contexts[user_id]
        if len(user_contexts) <= self.max_contexts_per_user:
            return
        
        # Sort by priority and access patterns, remove least important
        contexts_list = list(user_contexts.values())
        contexts_list.sort(
            key=lambda x: (x.priority.value, x.access_count, x.updated_at)
        )
        
        # Remove oldest, least accessed contexts
        contexts_to_remove = len(contexts_list) - self.max_contexts_per_user
        for i in range(contexts_to_remove):
            await self._remove_context(user_id, contexts_list[i].id)
        
        logger.debug(f"Removed {contexts_to_remove} old contexts for user {user_id}")
    
    async def _periodic_cleanup(self):
        """Periodic cleanup of expired contexts and conversations."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_hours * 3600)
                await self.cleanup_expired_contexts()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic cleanup: {e}")
    
    async def cleanup_expired_contexts(self):
        """Clean up expired contexts and conversations."""
        try:
            total_removed = 0
            
            # Clean up contexts
            for user_id in list(self.contexts.keys()):
                user_contexts = self.contexts[user_id]
                expired_ids = []
                
                for context_id, entry in user_contexts.items():
                    if entry.is_expired():
                        expired_ids.append(context_id)
                
                for context_id in expired_ids:
                    await self._remove_context(user_id, context_id)
                    total_removed += 1
                
                # Remove empty user context collections
                if not self.contexts[user_id]:
                    del self.contexts[user_id]
            
            # Clean up old conversations (older than 7 days)
            cutoff_time = datetime.utcnow() - timedelta(days=7)
            expired_conversations = []
            
            for conv_key, conversation in self.conversations.items():
                if conversation.last_updated < cutoff_time:
                    expired_conversations.append(conv_key)
            
            for conv_key in expired_conversations:
                del self.conversations[conv_key]
                total_removed += 1
            
            if total_removed > 0:
                logger.info(f"Cleaned up {total_removed} expired contexts and conversations")
                
        except Exception as e:
            logger.error(f"Error during context cleanup: {e}")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get context manager statistics."""
        try:
            total_contexts = sum(len(user_contexts) for user_contexts in self.contexts.values())
            
            context_by_type_counts = {}
            for context_type, context_ids in self.context_by_type.items():
                context_by_type_counts[context_type.value] = len(context_ids)
            
            return {
                "total_users": len(self.contexts),
                "total_contexts": total_contexts,
                "active_conversations": len(self.conversations),
                "contexts_by_type": context_by_type_counts,
                "total_tags": len(self.context_by_tags),
                "memory_usage": {
                    "contexts_mb": len(str(self.contexts)) / (1024 * 1024),
                    "conversations_mb": len(str(self.conversations)) / (1024 * 1024)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {"error": str(e)}


# Global context manager instance
_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """Get global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
    return _context_manager


async def initialize_context_manager(**kwargs) -> ContextManager:
    """Initialize and start the global context manager."""
    global _context_manager
    _context_manager = ContextManager(**kwargs)
    await _context_manager.start()
    return _context_manager


async def shutdown_context_manager():
    """Shutdown the global context manager."""
    global _context_manager
    if _context_manager:
        await _context_manager.stop()
        _context_manager = None