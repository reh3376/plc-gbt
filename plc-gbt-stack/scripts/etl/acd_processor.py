#!/usr/bin/env python3
"""
ACD Processor Module
Created: January 1, 2025
Purpose: Process Automation Control Database (.acd) files for PLC component extraction
"""

import os
import json
import logging
import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import zipfile
import tempfile
import hashlib

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

@dataclass
class ACDComponent:
    """Represents a component extracted from ACD file"""
    id: str
    name: str
    component_type: str  # DEVICE, WIRE, TERMINAL, SYMBOL, etc.
    manufacturer: Optional[str] = None
    catalog_number: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    properties: Dict[str, Any] = None
    connections: List[str] = None
    drawing_reference: Optional[str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}
        if self.connections is None:
            self.connections = []

@dataclass
class ACDDrawing:
    """Represents a drawing sheet from ACD file"""
    sheet_number: str
    title: str
    description: Optional[str] = None
    components: List[ACDComponent] = None
    wires: List[Dict[str, Any]] = None
    terminals: List[Dict[str, Any]] = None
    symbols: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.components is None:
            self.components = []
        if self.wires is None:
            self.wires = []
        if self.terminals is None:
            self.terminals = []
        if self.symbols is None:
            self.symbols = []

@dataclass
class ACDProject:
    """Represents complete ACD project data"""
    project_name: str
    version: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    drawings: List[ACDDrawing] = None
    components: List[ACDComponent] = None
    plc_references: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.drawings is None:
            self.drawings = []
        if self.components is None:
            self.components = []
        if self.plc_references is None:
            self.plc_references = []
        if self.metadata is None:
            self.metadata = {}

class ACDProcessor:
    """
    Processes Automation Control Database (.acd) files to extract PLC and automation components.
    
    ACD files typically contain:
    - PLC hardware configurations
    - I/O module definitions and mappings
    - Device catalogs and specifications
    - Network and communication configurations
    - Controller and rack layouts
    - Tag and variable definitions
    - Safety system configurations
    """
    
    def __init__(self):
        """Initialize ACD processor"""
        # Component type mappings for automation systems
        self.component_type_mappings = {
            'PLC': 'CONTROLLER',
            'CPU': 'CONTROLLER',
            'PROCESSOR': 'CONTROLLER',
            'IO_MODULE': 'IO_MODULE',
            'INPUT_MODULE': 'INPUT_MODULE',
            'OUTPUT_MODULE': 'OUTPUT_MODULE',
            'ANALOG_INPUT': 'ANALOG_MODULE',
            'ANALOG_OUTPUT': 'ANALOG_MODULE',
            'COMMUNICATION': 'COMM_MODULE',
            'ETHERNET': 'COMM_MODULE',
            'DEVICENET': 'COMM_MODULE',
            'CONTROLNET': 'COMM_MODULE',
            'PROFIBUS': 'COMM_MODULE',
            'RACK': 'CHASSIS',
            'CHASSIS': 'CHASSIS',
            'POWER_SUPPLY': 'POWER_SUPPLY',
            'HMI': 'HMI',
            'SAFETY': 'SAFETY_MODULE',
            'MOTION': 'MOTION_MODULE'
        }
        
        # PLC I/O patterns
        self.plc_io_patterns = [
            r'(\w+):I\.DATA\.(\d+)',     # ControlLogix format
            r'(\w+):O\.DATA\.(\d+)',     # Output format
            r'I:(\d+)/(\d+)',            # SLC format input
            r'O:(\d+)/(\d+)',            # SLC format output
            r'N(\d+):(\d+)',             # Integer file
            r'B(\d+):(\d+)',             # Binary file
            r'T(\d+):(\d+)',             # Timer file
            r'C(\d+):(\d+)',             # Counter file
        ]
        
        logger.info("ACDProcessor initialized")
    
    def process_file(self, file_path: str) -> ACDProject:
        """
        Process ACD file and extract component data.
        
        Args:
            file_path: Path to .acd file
            
        Returns:
            ACDProject with extracted components and metadata
        """
        logger.info("Processing ACD file", file_path=file_path)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ACD file not found: {file_path}")
            
        if not file_path.lower().endswith('.acd'):
            raise ValueError(f"Invalid file extension. Expected .acd, got: {file_path}")
            
        try:
            # ACD files are often compressed archives or XML-based
            if self._is_compressed_format(file_path):
                return self._process_compressed_acd(file_path)
            else:
                return self._process_xml_acd(file_path)
                
        except Exception as e:
            logger.error("Failed to process ACD file", file_path=file_path, error=str(e))
            raise
    
    def _is_compressed_format(self, file_path: str) -> bool:
        """Check if ACD file is in compressed format"""
        try:
            with zipfile.ZipFile(file_path, 'r'):
                return True
        except zipfile.BadZipFile:
            return False
    
    def _process_compressed_acd(self, file_path: str) -> ACDProject:
        """Process compressed ACD file format"""
        project_data = ACDProject(
            project_name=os.path.splitext(os.path.basename(file_path))[0],
            metadata={"file_path": file_path, "format": "compressed"}
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract compressed ACD
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                
            # Look for key files in extracted content
            extracted_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    extracted_files.append(os.path.join(root, file))
            
            logger.debug("Extracted ACD files", count=len(extracted_files))
            project_data.metadata["extracted_files"] = len(extracted_files)
            
            # Process main project files
            for file_path in extracted_files:
                file_ext = os.path.splitext(file_path)[1].lower()
                
                if file_ext in ['.xml', '.dwg', '.dxf']:
                    try:
                        self._process_drawing_file(file_path, project_data)
                    except Exception as e:
                        logger.warning("Failed to process drawing file", 
                                     file_path=file_path, error=str(e))
                        
                elif file_ext in ['.csv', '.txt']:
                    try:
                        self._process_component_list(file_path, project_data)
                    except Exception as e:
                        logger.warning("Failed to process component list", 
                                     file_path=file_path, error=str(e))
        
        return project_data
    
    def _process_xml_acd(self, file_path: str) -> ACDProject:
        """Process XML-based ACD file format"""
        project_data = ACDProject(
            project_name=os.path.splitext(os.path.basename(file_path))[0],
            metadata={"file_path": file_path, "format": "xml"}
        )
        
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Extract project metadata
            project_info = root.find('.//ProjectInfo')
            if project_info is not None:
                project_data.project_name = project_info.get('name', project_data.project_name)
                project_data.version = project_info.get('version')
                
                # Parse dates
                created = project_info.get('created')
                if created:
                    try:
                        project_data.created_date = datetime.fromisoformat(created)
                    except ValueError:
                        pass
                        
                modified = project_info.get('modified')  
                if modified:
                    try:
                        project_data.modified_date = datetime.fromisoformat(modified)
                    except ValueError:
                        pass
            
            # Extract drawings
            drawings = root.findall('.//Drawing')
            for drawing_elem in drawings:
                drawing = self._parse_drawing_element(drawing_elem)
                project_data.drawings.append(drawing)
                
            # Extract component catalog
            components = root.findall('.//Component')
            for comp_elem in components:
                component = self._parse_component_element(comp_elem)
                project_data.components.append(component)
                
            # Extract PLC references
            plc_refs = root.findall('.//PLCReference')
            for plc_ref in plc_refs:
                ref_data = {
                    'id': plc_ref.get('id'),
                    'address': plc_ref.get('address'),
                    'component': plc_ref.get('component'),
                    'description': plc_ref.get('description')
                }
                project_data.plc_references.append(ref_data)
                
        except ET.ParseError as e:
            logger.error("XML parsing failed", file_path=file_path, error=str(e))
            # Try to extract what we can from malformed XML
            project_data = self._fallback_text_parsing(file_path)
            
        return project_data
    
    def _parse_drawing_element(self, drawing_elem: ET.Element) -> ACDDrawing:
        """Parse drawing element from XML"""
        drawing = ACDDrawing(
            sheet_number=drawing_elem.get('sheet', 'Unknown'),
            title=drawing_elem.get('title', 'Untitled'),
            description=drawing_elem.get('description')
        )
        
        # Extract components from drawing
        components = drawing_elem.findall('.//Component')
        for comp_elem in components:
            component = self._parse_component_element(comp_elem)
            component.drawing_reference = drawing.sheet_number
            drawing.components.append(component)
            
        # Extract wires
        wires = drawing_elem.findall('.//Wire')
        for wire_elem in wires:
            wire_data = {
                'id': wire_elem.get('id'),
                'from': wire_elem.get('from'),
                'to': wire_elem.get('to'),
                'signal': wire_elem.get('signal'),
                'color': wire_elem.get('color')
            }
            drawing.wires.append(wire_data)
            
        # Extract terminals
        terminals = drawing_elem.findall('.//Terminal')
        for term_elem in terminals:
            terminal_data = {
                'id': term_elem.get('id'),
                'position': term_elem.get('position'),
                'signal': term_elem.get('signal'),
                'connection': term_elem.get('connection')
            }
            drawing.terminals.append(terminal_data)
            
        return drawing
    
    def _parse_component_element(self, comp_elem: ET.Element) -> ACDComponent:
        """Parse component element from XML"""
        component_id = comp_elem.get('id', self._generate_component_id())
        
        component = ACDComponent(
            id=component_id,
            name=comp_elem.get('name', f'Component_{component_id}'),
            component_type=self._map_component_type(comp_elem.get('type', 'UNKNOWN')),
            manufacturer=comp_elem.get('manufacturer'),
            catalog_number=comp_elem.get('catalog'),
            description=comp_elem.get('description'),
            location=comp_elem.get('location')
        )
        
        # Extract properties
        properties = comp_elem.find('.//Properties')
        if properties is not None:
            for prop in properties:
                component.properties[prop.tag] = prop.text
                
        # Extract connections
        connections = comp_elem.findall('.//Connection')
        for conn in connections:
            connection_ref = conn.get('ref') or conn.text
            if connection_ref:
                component.connections.append(connection_ref)
                
        return component
    
    def _process_drawing_file(self, file_path: str, project_data: ACDProject):
        """Process individual drawing file (DWG/DXF)"""
        # This would require a DWG/DXF parser library
        # For now, extract basic information from filename and attempt text extraction
        
        filename = os.path.basename(file_path)
        sheet_match = re.search(r'(\d+)', filename)
        sheet_number = sheet_match.group(1) if sheet_match else 'Unknown'
        
        drawing = ACDDrawing(
            sheet_number=sheet_number,
            title=filename,
            description=f"Drawing extracted from {filename}"
        )
        
        # Attempt to extract text-based component references
        if file_path.endswith('.txt') or file_path.endswith('.csv'):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    components = self._extract_components_from_text(content)
                    drawing.components.extend(components)
            except Exception as e:
                logger.warning("Failed to read drawing file", file_path=file_path, error=str(e))
                
        project_data.drawings.append(drawing)
    
    def _process_component_list(self, file_path: str, project_data: ACDProject):
        """Process component list file (CSV/TXT)"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if file_path.endswith('.csv'):
                components = self._parse_csv_components(content)
            else:
                components = self._extract_components_from_text(content)
                
            project_data.components.extend(components)
            
        except Exception as e:
            logger.error("Failed to process component list", file_path=file_path, error=str(e))
    
    def _parse_csv_components(self, csv_content: str) -> List[ACDComponent]:
        """Parse components from CSV content"""
        components = []
        lines = csv_content.strip().split('\n')
        
        if not lines:
            return components
            
        # Try to identify header row
        header = lines[0].lower().split(',')
        name_col = self._find_column_index(header, ['name', 'component', 'device'])
        type_col = self._find_column_index(header, ['type', 'category', 'kind'])
        desc_col = self._find_column_index(header, ['description', 'desc', 'details'])
        mfg_col = self._find_column_index(header, ['manufacturer', 'mfg', 'brand'])
        cat_col = self._find_column_index(header, ['catalog', 'part_number', 'part'])
        
        for i, line in enumerate(lines[1:], 1):
            try:
                fields = line.split(',')
                if len(fields) < 2:
                    continue
                    
                component = ACDComponent(
                    id=f"csv_comp_{i}",
                    name=fields[name_col] if name_col < len(fields) else f"Component_{i}",
                    component_type=self._map_component_type(
                        fields[type_col] if type_col < len(fields) else 'UNKNOWN'
                    ),
                    description=fields[desc_col] if desc_col < len(fields) else None,
                    manufacturer=fields[mfg_col] if mfg_col < len(fields) else None,
                    catalog_number=fields[cat_col] if cat_col < len(fields) else None
                )
                
                components.append(component)
                
            except Exception as e:
                logger.warning("Failed to parse CSV line", line_number=i+1, error=str(e))
                continue
                
        return components
    
    def _extract_components_from_text(self, text_content: str) -> List[ACDComponent]:
        """Extract components using text parsing patterns"""
        components = []
        
        # Common component patterns in automation control databases
        patterns = [
            # PLC addresses and I/O references
            (r'(\w+):([IO])\.DATA\.(\d+)', 'PLC_IO'),
            (r'Local:(\d+):([IO])\.DATA\.(\d+)', 'LOCAL_IO'),
            # Controller and rack references
            (r'Controller\[(\d+)\]', 'CONTROLLER'),
            (r'Chassis\[(\d+)\]', 'CHASSIS'),
            # I/O module references
            (r'Module\[(\d+)\]', 'IO_MODULE'),
            (r'Slot\[(\d+)\]', 'SLOT_REFERENCE'),
            # Network and communication
            (r'Network\[(\w+)\]', 'NETWORK'),
            (r'Device\[(\w+)\]', 'NETWORK_DEVICE'),
            # Safety and motion
            (r'Safety\[(\w+)\]', 'SAFETY_DEVICE'),
            (r'Axis\[(\d+)\]', 'MOTION_AXIS'),
        ]
        
        component_id = 0
        for pattern, comp_type in patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                component_id += 1
                component = ACDComponent(
                    id=f"text_comp_{component_id}",
                    name=match.group(0),
                    component_type=comp_type,
                    description=f"Extracted from text: {match.group(0)}"
                )
                
                # Extract additional context around the match
                start = max(0, match.start() - 50)
                end = min(len(text_content), match.end() + 50)
                context = text_content[start:end].strip()
                component.properties['context'] = context
                
                components.append(component)
                
        return components
    
    def _fallback_text_parsing(self, file_path: str) -> ACDProject:
        """Fallback text parsing for malformed ACD files"""
        project_data = ACDProject(
            project_name=os.path.splitext(os.path.basename(file_path))[0],
            metadata={"file_path": file_path, "format": "text_fallback"}
        )
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Extract components using text patterns
            components = self._extract_components_from_text(content)
            project_data.components.extend(components)
            
            # Extract PLC references
            plc_refs = self._extract_plc_references(content)
            project_data.plc_references.extend(plc_refs)
            
        except Exception as e:
            logger.error("Fallback parsing failed", file_path=file_path, error=str(e))
            
        return project_data
    
    def _extract_plc_references(self, content: str) -> List[Dict[str, Any]]:
        """Extract PLC I/O references from text"""
        references = []
        
        for pattern in self.plc_io_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for match in matches:
                ref_data = {
                    'id': f"plc_ref_{len(references)}",
                    'address': match.group(0),
                    'component': None,
                    'description': f"PLC reference: {match.group(0)}"
                }
                
                # Try to find associated component nearby
                start = max(0, match.start() - 100)
                end = min(len(content), match.end() + 100)
                context = content[start:end]
                
                # Look for component names in context
                comp_match = re.search(r'([A-Z]+\d+)', context)
                if comp_match:
                    ref_data['component'] = comp_match.group(1)
                    
                references.append(ref_data)
                
        return references
    
    def _find_column_index(self, header: List[str], possible_names: List[str]) -> int:
        """Find column index by matching possible names"""
        for i, col in enumerate(header):
            if any(name in col for name in possible_names):
                return i
        return 0  # Default to first column
    
    def _map_component_type(self, raw_type: str) -> str:
        """Map raw component type to standardized type"""
        if not raw_type:
            return 'UNKNOWN'
            
        raw_type_upper = raw_type.upper()
        
        for key, mapped_type in self.component_type_mappings.items():
            if key in raw_type_upper:
                return mapped_type
                
        return 'DEVICE'  # Default fallback
    
    def _generate_component_id(self) -> str:
        """Generate unique component ID"""
        return f"comp_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"
    
    def extract_plc_connections(self, project: ACDProject) -> List[Dict[str, Any]]:
        """
        Extract PLC connection mappings from ACD project.
        
        Returns list of PLC I/O mappings with component associations.
        """
        connections = []
        
        # Process PLC references
        for plc_ref in project.plc_references:
            connection = {
                'plc_address': plc_ref.get('address'),
                'component_id': plc_ref.get('component'),
                'description': plc_ref.get('description'),
                'io_type': self._determine_io_type(plc_ref.get('address', '')),
                'source': 'plc_reference'
            }
            connections.append(connection)
            
        # Extract from component properties
        for component in project.components:
            plc_addresses = []
            
            # Check component properties for PLC addresses
            for prop_name, prop_value in component.properties.items():
                if isinstance(prop_value, str):
                    for pattern in self.plc_io_patterns:
                        matches = re.findall(pattern, prop_value, re.IGNORECASE)
                        plc_addresses.extend(matches)
                        
            # Create connections for found addresses
            for address in plc_addresses:
                if isinstance(address, tuple):
                    address = ':'.join(str(x) for x in address)
                    
                connection = {
                    'plc_address': address,
                    'component_id': component.id,
                    'component_name': component.name,
                    'component_type': component.component_type,
                    'description': component.description,
                    'io_type': self._determine_io_type(address),
                    'source': 'component_properties'
                }
                connections.append(connection)
                
        return connections
    
    def _determine_io_type(self, address: str) -> str:
        """Determine I/O type from PLC address"""
        if not address:
            return 'UNKNOWN'
            
        address_upper = address.upper()
        
        if ':I.' in address_upper or 'I:' in address_upper:
            return 'INPUT'
        elif ':O.' in address_upper or 'O:' in address_upper:
            return 'OUTPUT'
        elif 'T' in address_upper and ':' in address_upper:
            return 'TIMER'
        elif 'C' in address_upper and ':' in address_upper:
            return 'COUNTER'
        elif 'N' in address_upper and ':' in address_upper:
            return 'INTEGER'
        elif 'B' in address_upper and ':' in address_upper:
            return 'BINARY'
        else:
            return 'UNKNOWN'
    
    def generate_summary(self, project: ACDProject) -> Dict[str, Any]:
        """Generate summary statistics for ACD project"""
        summary = {
            'project_name': project.project_name,
            'drawings_count': len(project.drawings),
            'components_count': len(project.components),
            'plc_references_count': len(project.plc_references),
            'component_types': {},
            'manufacturers': {},
            'plc_io_types': {},
            'created_date': project.created_date.isoformat() if project.created_date else None,
            'modified_date': project.modified_date.isoformat() if project.modified_date else None
        }
        
        # Component type distribution
        for component in project.components:
            comp_type = component.component_type
            summary['component_types'][comp_type] = summary['component_types'].get(comp_type, 0) + 1
            
            if component.manufacturer:
                mfg = component.manufacturer
                summary['manufacturers'][mfg] = summary['manufacturers'].get(mfg, 0) + 1
                
        # PLC I/O type distribution  
        connections = self.extract_plc_connections(project)
        for conn in connections:
            io_type = conn.get('io_type', 'UNKNOWN')
            summary['plc_io_types'][io_type] = summary['plc_io_types'].get(io_type, 0) + 1
            
        return summary

# Convenience functions for common operations
def process_acd_file(file_path: str) -> ACDProject:
    """Convenience function to process ACD file"""
    processor = ACDProcessor()
    return processor.process_file(file_path)

def extract_components(file_path: str) -> List[ACDComponent]:
    """Extract just components from ACD file"""
    project = process_acd_file(file_path)
    return project.components

def extract_plc_mappings(file_path: str) -> List[Dict[str, Any]]:
    """Extract PLC I/O mappings from ACD file"""
    processor = ACDProcessor()
    project = processor.process_file(file_path)
    return processor.extract_plc_connections(project) 