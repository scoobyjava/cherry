from typing import Dict, Any, List, Optional, Tuple
import asyncio
import uuid
import logging
from datetime import datetime
import json

import numpy as np
import psycopg2
from psycopg2.extras import Json, RealDictCursor
import pinecone
from sentence_transformers import SentenceTransformer
import openai

logger = logging.getLogger(__name__)

class UIUXAgent:
    """
    Agent responsible for UI/UX design recommendations, wireframing, and design reviews.
    Helps create user-friendly and aesthetically pleasing interfaces based on requirements.
    """

    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the UIUXAgent with optional configuration.
        
        Args:
            agent_id: Unique identifier for the agent
            config: Configuration dictionary for the agent
        """
        self.agent_id = agent_id
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.logger.info("UIUXAgent initialized")
        self.embedding_model = None
        self.pg_conn_string = config.get('postgres_connection_string') if config else None
        self.pinecone_api_key = config.get('pinecone_api_key') if config else None
        self.pinecone_environment = config.get('pinecone_environment') if config else None
        self.pinecone_index_name = config.get('pinecone_index_name') if config else None
        self.openai_api_key = config.get('openai_api_key', os.environ.get('OPENAI_API_KEY'))
        self.embedding_model = config.get('embedding_model', 'text-embedding-ada-002')
        
        # Initialize connections
        self.pinecone_client = None
        self.pg_conn = None

    async def initialize(self) -> None:
        """Initialize resources needed for UI/UX recommendations and embedding storage."""
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize Pinecone
            if self.pinecone_api_key and self.pinecone_environment:
                pinecone.init(api_key=self.pinecone_api_key, environment=self.pinecone_environment)
                if self.pinecone_index_name not in pinecone.list_indexes():
                    logger.warning(f"Pinecone index {self.pinecone_index_name} does not exist")
            else:
                logger.warning("Pinecone credentials not provided")
            
            # Initialize OpenAI
            openai.api_key = self.openai_api_key
            
            # Initialize PostgreSQL connection
            self.pg_conn = psycopg2.connect(self.pg_conn_string)
            
        except Exception as e:
            logger.error(f"Error initializing UIUXAgent: {str(e)}")
            raise

    async def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embeddings for UI/UX recommendations.
        
        Args:
            text: The UI/UX recommendation text to generate embeddings for
            
        Returns:
            A numpy array containing the embedding vector
            
        Raises:
            ValueError: If text is empty or model is not initialized
        """
        if not text.strip():
            raise ValueError("Cannot generate embedding for empty text")
        
        if self.embedding_model is None:
            raise ValueError("Embedding model not initialized")
        
        try:
            # Generate embedding using the model
            embedding = self.embedding_model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    async def store_recommendation_in_postgres(
        self, 
        recommendation: str, 
        metadata: Dict[str, Any]
    ) -> str:
        """
        Store UI/UX recommendation and metadata in PostgreSQL.
        
        Args:
            recommendation: The UI/UX recommendation text
            metadata: Dictionary containing metadata about the recommendation
            
        Returns:
            The UUID of the stored recommendation
            
        Raises:
            ValueError: If database connection string is not provided
            Exception: For database errors
        """
        if not self.pg_conn_string:
            raise ValueError("PostgreSQL connection string not provided")
        
        # Generate a UUID for this recommendation
        memory_id = str(uuid.uuid4())
        
        # Prepare data for insertion
        current_time = datetime.now().isoformat()
        
        try:
            conn = psycopg2.connect(self.pg_conn_string)
            cursor = conn.cursor()
            
            # Begin transaction
            conn.autocommit = False
            
            try:
                # Insert into memories table
                cursor.execute(
                    """
                    INSERT INTO memories
                    (id, content, metadata, created_at, agent_id, memory_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        memory_id, 
                        recommendation, 
                        Json(metadata), 
                        current_time, 
                        self.agent_id, 
                        'uiux_recommendation'
                    )
                )
                
                # Commit transaction
                conn.commit()
                logger.info(f"Successfully stored UI/UX recommendation with ID: {memory_id}")
                return memory_id
                
            except Exception as e:
                # Rollback in case of error
                conn.rollback()
                logger.error(f"Transaction failed, rolling back: {str(e)}")
                raise
            
            finally:
                cursor.close()
                conn.close()
                
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise

    async def insert_embedding_in_pinecone(
        self, 
        memory_id: str, 
        embedding: np.ndarray, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Insert embedding into Pinecone with memory ID matching PostgreSQL record.
        
        Args:
            memory_id: UUID of the recommendation in PostgreSQL
            embedding: The embedding vector
            metadata: Metadata to store with the embedding
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If Pinecone credentials are missing
            Exception: For Pinecone API errors
        """
        if not (self.pinecone_api_key and self.pinecone_environment and self.pinecone_index_name):
            raise ValueError("Pinecone credentials or index name not provided")
        
        try:
            # Get the index
            index = pinecone.Index(self.pinecone_index_name)
            
            # Convert numpy array to list for Pinecone
            embedding_list = embedding.tolist()
            
            # Add namespace to metadata
            metadata.update({
                "agent_id": self.agent_id,
                "memory_type": "uiux_recommendation",
                "created_at": datetime.now().isoformat()
            })
            
            # Upsert the vector
            upsert_response = index.upsert(
                vectors=[(memory_id, embedding_list, metadata)],
                namespace="uiux_recommendations"
            )
            
            logger.info(f"Successfully inserted embedding in Pinecone with ID: {memory_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error inserting embedding in Pinecone: {str(e)}")
            raise

    async def process_and_store_recommendation(
        self, 
        recommendation: str, 
        metadata: Dict[str, Any]
    ) -> Tuple[str, bool]:
        """
        Process a UI/UX recommendation, store in PostgreSQL and Pinecone.
        
        Args:
            recommendation: The UI/UX recommendation text
            metadata: Dictionary containing metadata about the recommendation
            
        Returns:
            Tuple containing (memory_id, success_status)
            
        Raises:
            Exception: For any errors during processing
        """
        try:
            # Generate embedding
            embedding = await self.generate_embedding(recommendation)
            
            # Store in PostgreSQL
            memory_id = await self.store_recommendation_in_postgres(recommendation, metadata)
            
            # Store in Pinecone
            pinecone_success = await self.insert_embedding_in_pinecone(memory_id, embedding, metadata)
            
            return memory_id, pinecone_success
            
        except Exception as e:
            logger.error(f"Error processing and storing recommendation: {str(e)}")
            raise
            
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process UI/UX recommendation requests."""
        if 'recommendation' not in request:
            return {"status": "error", "message": "Recommendation is required"}
        
        recommendation = request['recommendation']
        metadata = request.get('metadata', {})
        
        try:
            memory_id, pinecone_success = await self.process_and_store_recommendation(
                recommendation, metadata
            )
            
            return {
                "status": "success",
                "memory_id": memory_id,
                "pinecone_success": pinecone_success,
                "agent_id": self.agent_id
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "agent_id": self.agent_id
            }

    async def retrieve_design_memories(self, query: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieve design memories based on the query.
        
        Args:
            query (str): The search query text
            top_n (int): Number of top memories to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of design memory records with recommendations, wireframes, etc.
        """
        # 1. Generate embeddings for the query using OpenAI
        response = openai.Embedding.create(
            input=query,
            model=self.embedding_model
        )
        query_embedding = response['data'][0]['embedding']
        
        # 2. Query Pinecone for similar vectors
        results = self.pinecone_client.query(
            vector=query_embedding,
            top_k=top_n,
            include_metadata=True
        )
        
        # Extract memory IDs from results
        memory_ids = [match['id'] for match in results['matches']]
        
        if not memory_ids:
            return []
            
        # 3. Retrieve full records from PostgreSQL
        cursor = self.pg_conn.cursor(cursor_factory=RealDictCursor)
        
        # Convert list to tuple for SQL IN clause
        memory_ids_tuple = tuple(memory_ids)
        
        # Handle case with only one ID
        if len(memory_ids) == 1:
            query = "SELECT * FROM ui_ux_memories WHERE id = %s"
            cursor.execute(query, (memory_ids[0],))
        else:
            placeholders = ', '.join(['%s'] * len(memory_ids))
            query = f"SELECT * FROM ui_ux_memories WHERE id IN ({placeholders})"
            cursor.execute(query, memory_ids)
            
        # Fetch all records
        records = cursor.fetchall()
        cursor.close()
        
        # 4. Process and return structured data
        memories = []
        for record in records:
            # Convert database record to dictionary
            memory = dict(record)
            
            # Parse JSON fields if needed
            if isinstance(memory.get('recommendations'), str):
                memory['recommendations'] = json.loads(memory['recommendations'])
                
            if isinstance(memory.get('wireframes'), str):
                memory['wireframes'] = json.loads(memory['wireframes'])
                
            # Format dates for serialization
            if 'created_at' in memory and isinstance(memory['created_at'], datetime):
                memory['created_at'] = memory['created_at'].isoformat()
                
            memories.append(memory)
            
        # Order results to match the original vector similarity ranking
        ordered_memories = []
        for memory_id in memory_ids:
            for memory in memories:
                if memory['id'] == memory_id:
                    ordered_memories.append(memory)
                    break
                    
        return ordered_memories

    def generate_ui_recommendations(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Provides detailed UI recommendations based on project requirements.
        
        Args:
            requirements: Dictionary containing project requirements and constraints
                Expected keys:
                - 'target_audience': Description of the target users
                - 'brand_identity': Brand guidelines or identity information
                - 'device_targets': List of target devices (mobile, desktop, etc.)
                - 'accessibility_needs': Accessibility requirements
        
        Returns:
            Dictionary containing detailed UI recommendations:
            - 'color_scheme': Recommended color palette with hex codes
            - 'typography': Font families and sizing recommendations
            - 'layout_principles': Layout guidelines and principles
            - 'interaction_patterns': Recommended UI interaction patterns
            - 'accessibility_features': Specific accessibility implementations
        """
        self.logger.info(f"Generating UI recommendations based on requirements: {requirements}")
        
        # Implementation would process requirements and generate specific recommendations
        # Placeholder for actual implementation
        recommendations = {
            'color_scheme': {
                'primary': '#4A90E2',
                'secondary': '#50E3C2',
                'accent': '#F5A623',
                'background': '#FFFFFF',
                'text': '#333333',
            },
            'typography': {
                'heading_font': 'Poppins',
                'body_font': 'Inter',
                'size_scale': {
                    'h1': '2.5rem',
                    'h2': '2rem',
                    'h3': '1.75rem',
                    'body': '1rem',
                    'small': '0.875rem'
                }
            },
            'layout_principles': {
                'grid_system': '12-column responsive grid',
                'spacing': 'Consistent 8px spacing scale',
                'alignment': 'Left-aligned content with consistent margins'
            },
            'interaction_patterns': {
                'navigation': 'Persistent top navigation with dropdown menus',
                'buttons': 'Clearly labeled with hover states',
                'forms': 'Single column with inline validation'
            },
            'accessibility_features': {
                'contrast_ratios': 'AA compliance for all text',
                'keyboard_navigation': 'Fully navigable with keyboard',
                'screen_reader': 'All elements properly labeled for screen readers'
            }
        }
        
        return recommendations

    def generate_wireframe(self, project_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates structured wireframes or mock-up specifications for websites/apps.
        
        Args:
            project_details: Dictionary containing project details required for wireframing
                Expected keys:
                - 'pages': List of pages/screens needed
                - 'user_flows': Key user journeys through the interface
                - 'content_requirements': Content blocks and information architecture
                - 'functional_requirements': Interactive elements needed
        
        Returns:
            Dictionary containing wireframe specifications:
            - 'screens': Array of screen definitions with layout information
            - 'components': Reusable UI components in the wireframe
            - 'navigation_map': How screens connect to each other
            - 'annotations': Notes about functionality and behavior
            - 'responsive_variants': How layouts adapt to different screen sizes
        """
        self.logger.info(f"Generating wireframe based on project details: {project_details}")
        
        # Implementation would process project details and generate wireframe specifications
        # Placeholder for actual implementation
        wireframe = {
            'screens': [
                {
                    'name': 'Home Page',
                    'layout': {
                        'header': {'height': '80px', 'content': ['logo', 'navigation']},
                        'hero': {'height': '500px', 'content': ['headline', 'cta_button', 'hero_image']},
                        'features_section': {'layout': 'grid', 'columns': 3, 'items': ['feature_1', 'feature_2', 'feature_3']},
                        'footer': {'height': '200px', 'content': ['links', 'social', 'legal']}
                    }
                },
                # Additional screens would be defined here
            ],
            'components': {
                'navigation': {'type': 'horizontal_menu', 'items': ['Home', 'Features', 'Pricing', 'Contact']},
                'cta_button': {'type': 'button', 'style': 'primary', 'label': 'Get Started'},
                # Additional components would be defined here
            },
            'navigation_map': {
                'Home': ['Features', 'Pricing', 'Contact'],
                'Features': ['Home', 'Pricing'],
                # Additional navigation connections would be defined here
            },
            'annotations': {
                'cta_button': 'Should be prominently displayed with high contrast',
                'navigation': 'Should collapse to hamburger menu on mobile',
                # Additional annotations would be defined here
            },
            'responsive_variants': {
                'mobile': {
                    'navigation': 'hamburger_menu',
                    'features_section': {'layout': 'stack', 'columns': 1}
                },
                'tablet': {
                    'features_section': {'layout': 'grid', 'columns': 2}
                }
                # Additional responsive variations would be defined here
            }
        }
        
        return wireframe

    def review_existing_design(self, design: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reviews provided designs and suggests specific improvements for usability and aesthetic quality.
        
        Args:
            design: Dictionary containing the design to be reviewed
                Expected keys:
                - 'screenshots': URLs or image data of design screens
                - 'style_guide': Current style guide if available
                - 'user_testing_results': Any existing user testing data
                - 'target_metrics': What the design aims to improve
        
        Returns:
            Dictionary containing design review results:
            - 'strengths': Positive aspects of the current design
            - 'improvement_areas': Areas that need refinement
            - 'specific_recommendations': Concrete suggestions for each improvement area
            - 'priority': Recommended order to address improvements
            - 'visual_examples': Reference examples for suggested improvements
        """
        self.logger.info(f"Reviewing existing design: {design.get('name', 'Unnamed design')}")
        
        # Implementation would analyze the provided design and generate improvement recommendations
        # Placeholder for actual implementation
        review_results = {
            'strengths': [
                {'aspect': 'Color palette', 'details': 'Good use of brand colors with sufficient contrast'},
                {'aspect': 'Typography', 'details': 'Clear hierarchy in most sections'},
                {'aspect': 'Layout', 'details': 'Clean and organized structure'}
            ],
            'improvement_areas': [
                {'aspect': 'Navigation', 'details': 'Menu structure is overly complex'},
                {'aspect': 'Call-to-actions', 'details': 'CTAs lack visual prominence'},
                {'aspect': 'Mobile responsiveness', 'details': 'Layout breaks on smaller screens'},
                {'aspect': 'Form design', 'details': 'Input fields lack clear validation states'}
            ],
            'specific_recommendations': {
                'navigation': [
                    'Reduce top-level menu items to 5 or fewer',
                    'Add visual indicators for current page',
                    'Improve dropdown menu accessibility'
                ],
                'call-to-actions': [
                    'Increase button size by 20%',
                    'Use more distinctive color for primary actions',
                    'Add hover states to all interactive elements'
                ],
                'mobile_responsiveness': [
                    'Implement proper breakpoints at 768px and 480px',
                    'Stack grid items on smaller screens',
                    'Increase touch targets to minimum 44px height'
                ],
                'form_design': [
                    'Add inline validation with clear error messages',
                    'Group related fields visually',
                    'Simplify form by removing unnecessary fields'
                ]
            },
            'priority': [
                'mobile_responsiveness',
                'call-to-actions',
                'form_design',
                'navigation'
            ],
            'visual_examples': {
                'navigation': 'https://example.com/improved-navigation.png',
                'call-to-actions': 'https://example.com/improved-cta.png',
                'mobile_responsiveness': 'https://example.com/improved-mobile.png',
                'form_design': 'https://example.com/improved-form.png'
            }
        }
        
        return review_results

    async def share_memory_content(
        self, 
        recipient_agent_id: str, 
        content_ids: List[str] = None,
        content_query: str = None,
        tag_name: str = None
    ) -> Dict[str, Any]:
        """
        Share UI/UX related memory content with another agent by tagging it.
        
        Args:
            recipient_agent_id: ID of the agent to share with
            content_ids: Optional specific memory content IDs to share
            content_query: Optional query to find relevant content to share
            tag_name: Optional custom tag name, defaults to a generated tag
            
        Returns:
            Dict containing status and shared content information
        """
        if not content_ids and not content_query:
            return {"status": "error", "message": "Either content_ids or content_query must be provided"}
        
        # If no custom tag provided, create a descriptive one
        if not tag_name:
            tag_name = f"uiux_shared_{recipient_agent_id}_{uuid.uuid4().hex[:8]}"
        
        # Find content to share if query provided
        if content_query and not content_ids:
            # First check Postgres for relevant information
            postgres_results = await self.postgres_memory.search(content_query)
            # Then check Pinecone for semantic matches
            pinecone_results = await self.pinecone_memory.semantic_search(content_query)
            
            # Extract IDs from results
            content_ids = []
            if postgres_results:
                content_ids.extend([item.get('id') for item in postgres_results if 'id' in item])
            if pinecone_results:
                content_ids.extend([item.get('id') for item in pinecone_results if 'id' in item])
                
            # Remove duplicates
            content_ids = list(set(content_ids))
        
        if not content_ids:
            return {"status": "warning", "message": "No content found to share"}
        
        # Tag content in both memory systems
        postgres_results = await self._tag_in_postgres(content_ids, recipient_agent_id, tag_name)
        pinecone_results = await self._tag_in_pinecone(content_ids, recipient_agent_id, tag_name)
        
        return {
            "status": "success",
            "tag_name": tag_name,
            "recipient_agent_id": recipient_agent_id,
            "content_ids": content_ids,
            "postgres_tagged": postgres_results,
            "pinecone_tagged": pinecone_results
        }
    
    async def _tag_in_postgres(
        self, 
        content_ids: List[str], 
        recipient_agent_id: str, 
        tag_name: str
    ) -> Dict[str, Any]:
        """
        Tag content in PostgreSQL with sharing information.
        
        Args:
            content_ids: IDs of content to tag
            recipient_agent_id: ID of recipient agent
            tag_name: Tag name to apply
            
        Returns:
            Dict with results of tagging operation
        """
        tagged_ids = []
        
        for content_id in content_ids:
            try:
                # Get existing metadata
                content = await self.postgres_memory.get_by_id(content_id)
                if not content:
                    continue
                
                # Update metadata with sharing information
                metadata = content.get('metadata', {})
                if not metadata:
                    metadata = {}
                
                # Add or update tags
                if 'tags' not in metadata:
                    metadata['tags'] = []
                
                # Add the new tag
                metadata['tags'].append(tag_name)
                
                # Add sharing information
                if 'shared_with' not in metadata:
                    metadata['shared_with'] = []
                
                sharing_info = {
                    'agent_id': recipient_agent_id,
                    'tag': tag_name,
                    'timestamp': asyncio.get_event_loop().time()
                }
                metadata['shared_with'].append(sharing_info)
                
                # Update the content with new metadata
                await self.postgres_memory.update(content_id, {"metadata": metadata})
                tagged_ids.append(content_id)
                
            except Exception as e:
                print(f"Error tagging PostgreSQL content {content_id}: {str(e)}")
        
        return {
            "success": len(tagged_ids),
            "failed": len(content_ids) - len(tagged_ids),
            "tagged_ids": tagged_ids
        }
    
    async def _tag_in_pinecone(
        self, 
        content_ids: List[str], 
        recipient_agent_id: str, 
        tag_name: str
    ) -> Dict[str, Any]:
        """
        Tag content in Pinecone with sharing information.
        
        Args:
            content_ids: IDs of content to tag
            recipient_agent_id: ID of recipient agent
            tag_name: Tag name to apply
            
        Returns:
            Dict with results of tagging operation
        """
        tagged_ids = []
        
        for content_id in content_ids:
            try:
                # Get existing vector and metadata
                vector_data = await self.pinecone_memory.get_by_id(content_id)
                if not vector_data:
                    continue
                
                # Update metadata with sharing information
                metadata = vector_data.get('metadata', {})
                if not metadata:
                    metadata = {}
                
                # Add or update tags
                if 'tags' not in metadata:
                    metadata['tags'] = []
                
                # Add the new tag
                metadata['tags'].append(tag_name)
                
                # Add sharing information
                if 'shared_with' not in metadata:
                    metadata['shared_with'] = []
                
                sharing_info = {
                    'agent_id': recipient_agent_id,
                    'tag': tag_name,
                    'timestamp': asyncio.get_event_loop().time()
                }
                metadata['shared_with'].append(sharing_info)
                
                # Update the vector with new metadata
                await self.pinecone_memory.update_metadata(content_id, metadata)
                tagged_ids.append(content_id)
                
            except Exception as e:
                print(f"Error tagging Pinecone content {content_id}: {str(e)}")
        
        return {
            "success": len(tagged_ids),
            "failed": len(content_ids) - len(tagged_ids),
            "tagged_ids": tagged_ids
        }
    
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process UI/UX related requests."""
        request_type = request.get('type')
        
        if request_type == 'share_memory':
            return await self.share_memory_content(
                recipient_agent_id=request.get('recipient_agent_id'),
                content_ids=request.get('content_ids'),
                content_query=request.get('content_query'),
                tag_name=request.get('tag_name')
            )
        
        # Other UI/UX related requests can be handled here
        
        return {"status": "error", "message": f"Unknown request type: {request_type}"}
