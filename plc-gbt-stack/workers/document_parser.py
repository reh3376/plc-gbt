#!/usr/bin/env python3
"""
PLC Document Parser Module
Created: January 1, 2025
Purpose: Extract data from PDF and L5X files for PLC knowledge graph
"""

import hashlib
import logging
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# PDF processing
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    logging.warning("pdfplumber not available - PDF parsing disabled")

# XML processing for L5X files

@dataclass
class ExtractedDocument:
    """Container for extracted document data"""
    file_path: str
    file_type: str
    metadata: Dict[str, Any]
    content: Dict[str, Any]
    checksum: str
    extracted_at: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "file_path": self.file_path,
            "file_type": self.file_type,
            "metadata": self.metadata,
            "content": self.content,
            "checksum": self.checksum,
            "extracted_at": self.extracted_at.isoformat()
        }

@dataclass
class PLCProgram:
    """PLC Program data structure"""
    name: str
    firmware: str
    project: str
    routines: List[Dict[str, Any]]
    aois: List[Dict[str, Any]]
    udts: List[Dict[str, Any]]
    tags: List[Dict[str, Any]]
    devices: List[Dict[str, Any]]

@dataclass
class SpecificationDocument:
    """Specification document data structure"""
    title: str
    doc_type: str
    version: str
    content_sections: List[Dict[str, Any]]
    page_count: int
    qa_pairs: List[Dict[str, Any]]

class DocumentParser:
    """Main document parser class"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def calculate_checksum(self, file_path: str) -> str:
        """Calculate MD5 checksum for file"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum for {file_path}: {e}")
            return ""

    def parse_document(self, file_path: str) -> Optional[ExtractedDocument]:
        """Main entry point for document parsing"""
        if not os.path.exists(file_path):
            self.logger.error(f"File not found: {file_path}")
            return None

        file_ext = os.path.splitext(file_path)[1].lower()

        try:
            if file_ext == '.pdf':
                return self._parse_pdf(file_path)
            elif file_ext == '.l5x':
                return self._parse_l5x(file_path)
            elif file_ext == '.acd':
                return self._parse_acd(file_path)
            else:
                self.logger.warning(f"Unsupported file type: {file_ext}")
                return None

        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return None

    def _parse_pdf(self, file_path: str) -> Optional[ExtractedDocument]:
        """Parse PDF specification documents"""
        if not PDF_AVAILABLE:
            self.logger.error("PDF parsing not available - install pdfplumber")
            return None

        try:
            with pdfplumber.open(file_path) as pdf:
                metadata = {
                    "page_count": len(pdf.pages),
                    "title": pdf.metadata.get('Title', ''),
                    "author": pdf.metadata.get('Author', ''),
                    "creator": pdf.metadata.get('Creator', ''),
                    "creation_date": str(pdf.metadata.get('CreationDate', '')),
                    "modification_date": str(pdf.metadata.get('ModDate', ''))
                }

                # Extract text content by page
                pages_content = []
                full_text = ""

                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    pages_content.append({
                        "page_number": i + 1,
                        "text": page_text,
                        "word_count": len(page_text.split())
                    })
                    full_text += f"\n{page_text}"

                # Extract potential Q&A pairs using simple heuristics
                qa_pairs = self._extract_qa_pairs_from_text(full_text)

                # Identify document type based on content
                doc_type = self._identify_document_type(full_text, metadata.get('title', ''))

                content = {
                    "pages": pages_content,
                    "full_text": full_text.strip(),
                    "qa_pairs": qa_pairs,
                    "doc_type": doc_type,
                    "word_count": len(full_text.split()),
                    "sections": self._extract_sections_from_text(full_text)
                }

                return ExtractedDocument(
                    file_path=file_path,
                    file_type="PDF",
                    metadata=metadata,
                    content=content,
                    checksum=self.calculate_checksum(file_path),
                    extracted_at=datetime.now()
                )

        except Exception as e:
            self.logger.error(f"Error parsing PDF {file_path}: {e}")
            return None

    def _parse_l5x(self, file_path: str) -> Optional[ExtractedDocument]:
        """Parse L5X PLC program files"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Extract basic program information
            metadata = {
                "schema_revision": root.get('SchemaRevision', ''),
                "software_revision": root.get('SoftwareRevision', ''),
                "target_name": root.get('TargetName', ''),
                "target_type": root.get('TargetType', ''),
                "contains_context": root.get('ContainsContext', ''),
                "export_date": root.get('ExportDate', ''),
                "export_options": root.get('ExportOptions', '')
            }

            # Extract controller information
            controller = root.find('.//Controller')
            if controller is not None:
                controller_info = {
                    "name": controller.get('Name', ''),
                    "processor_type": controller.get('ProcessorType', ''),
                    "major_revision": controller.get('MajorRev', ''),
                    "minor_revision": controller.get('MinorRev', ''),
                    "time_slice": controller.get('TimeSlice', ''),
                    "share_unused_time_slice": controller.get('ShareUnusedTimeSlice', '')
                }
                metadata["controller"] = controller_info

            # Parse PLC components
            routines = self._extract_routines(root)
            aois = self._extract_aois(root)
            udts = self._extract_udts(root)
            tags = self._extract_tags(root)
            devices = self._extract_devices(root)

            # Create PLC program structure
            plc_program = PLCProgram(
                name=metadata.get("controller", {}).get("name", "Unknown"),
                firmware=f"v{metadata.get('software_revision', '')}",
                project=os.path.splitext(os.path.basename(file_path))[0],
                routines=routines,
                aois=aois,
                udts=udts,
                tags=tags,
                devices=devices
            )

            content = {
                "plc_program": plc_program.__dict__,
                "component_counts": {
                    "routines": len(routines),
                    "aois": len(aois),
                    "udts": len(udts),
                    "tags": len(tags),
                    "devices": len(devices)
                },
                "raw_xml_size": os.path.getsize(file_path)
            }

            return ExtractedDocument(
                file_path=file_path,
                file_type="L5X",
                metadata=metadata,
                content=content,
                checksum=self.calculate_checksum(file_path),
                extracted_at=datetime.now()
            )

        except ET.ParseError as e:
            self.logger.error(f"XML parsing error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing L5X {file_path}: {e}")
            return None

    def _parse_acd(self, file_path: str) -> Optional[ExtractedDocument]:
        """Parse Automation Control Database (.acd) file"""
        import os
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'etl'))
        from acd_processor import ACDProcessor

        self.logger.info(f"Parsing ACD file: {file_path}")

        try:
            processor = ACDProcessor()
            acd_project = processor.process_file(file_path)

            # Convert ACD project to ExtractedDocument format
            metadata = {
                "project_name": acd_project.project_name,
                "version": acd_project.version,
                "created_date": acd_project.created_date.isoformat() if acd_project.created_date else None,
                "modified_date": acd_project.modified_date.isoformat() if acd_project.modified_date else None,
                "format": acd_project.metadata.get("format", "unknown"),
                "file_size": os.path.getsize(file_path),
                "total_drawings": len(acd_project.drawings),
                "total_components": len(acd_project.components),
                "total_plc_references": len(acd_project.plc_references)
            }

            content = {
                "project_name": acd_project.project_name,
                "drawings": [self._convert_acd_drawing(drawing) for drawing in acd_project.drawings],
                "components": [self._convert_acd_component(comp) for comp in acd_project.components],
                "plc_references": acd_project.plc_references,
                "plc_connections": processor.extract_plc_connections(acd_project),
                "summary": processor.generate_summary(acd_project),
                "component_counts": {
                    "drawings": len(acd_project.drawings),
                    "components": len(acd_project.components),
                    "plc_references": len(acd_project.plc_references)
                }
            }

            extracted_doc = ExtractedDocument(
                file_path=file_path,
                file_type="ACD",
                metadata=metadata,
                content=content,
                checksum=self.calculate_checksum(file_path),
                extracted_at=datetime.now()
            )

            self.logger.info(f"ACD parsing completed: {len(acd_project.drawings)} drawings, {len(acd_project.components)} components")

            return extracted_doc

        except Exception as e:
            self.logger.error(f"Error parsing ACD {file_path}: {e}")
            return None

    def _convert_acd_drawing(self, drawing) -> Dict[str, Any]:
        """Convert ACD drawing to dictionary format"""
        return {
            "sheet_number": drawing.sheet_number,
            "title": drawing.title,
            "description": drawing.description,
            "components": [self._convert_acd_component(comp) for comp in drawing.components],
            "wires": drawing.wires,
            "terminals": drawing.terminals,
            "symbols": drawing.symbols
        }

    def _convert_acd_component(self, component) -> Dict[str, Any]:
        """Convert ACD component to dictionary format"""
        return {
            "id": component.id,
            "name": component.name,
            "component_type": component.component_type,
            "manufacturer": component.manufacturer,
            "catalog_number": component.catalog_number,
            "description": component.description,
            "location": component.location,
            "properties": component.properties,
            "connections": component.connections,
            "drawing_reference": component.drawing_reference
        }

    def _extract_routines(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract routine information from L5X"""
        routines = []

        for routine in root.findall('.//Routine'):
            routine_data = {
                "name": routine.get('Name', ''),
                "type": routine.get('Type', ''),
                "language": self._get_routine_language(routine),
                "description": self._get_description(routine),
                "parameters": self._extract_routine_parameters(routine),
                "local_tags": self._extract_local_tags(routine)
            }
            routines.append(routine_data)

        return routines

    def _extract_aois(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract Add-On Instruction information from L5X"""
        aois = []

        for aoi in root.findall('.//AddOnInstructionDefinition'):
            aoi_data = {
                "name": aoi.get('Name', ''),
                "revision": aoi.get('Revision', ''),
                "vendor": aoi.get('Vendor', ''),
                "execution_context": aoi.get('ExecutePrescan', ''),
                "description": self._get_description(aoi),
                "parameters": self._extract_aoi_parameters(aoi),
                "local_tags": self._extract_aoi_local_tags(aoi)
            }
            aois.append(aoi_data)

        return aois

    def _extract_udts(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract User Defined Type information from L5X"""
        udts = []

        for udt in root.findall('.//DataType'):
            if udt.get('Family') == 'NoFamily':  # UDT indicator
                udt_data = {
                    "name": udt.get('Name', ''),
                    "family": udt.get('Family', ''),
                    "class": udt.get('Class', ''),
                    "description": self._get_description(udt),
                    "members": self._extract_udt_members(udt),
                    "size": self._calculate_udt_size(udt)
                }
                udts.append(udt_data)

        return udts

    def _extract_tags(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract tag information from L5X"""
        tags = []

        for tag in root.findall('.//Tag'):
            tag_data = {
                "name": tag.get('Name', ''),
                "tag_type": tag.get('TagType', ''),
                "data_type": tag.get('DataType', ''),
                "dimensions": tag.get('Dimensions', ''),
                "radix": tag.get('Radix', ''),
                "external_access": tag.get('ExternalAccess', ''),
                "description": self._get_description(tag),
                "usage": tag.get('Usage', ''),
                "alias_for": tag.get('AliasFor', '') if tag.get('AliasFor') else None
            }
            tags.append(tag_data)

        return tags

    def _extract_devices(self, root: ET.Element) -> List[Dict[str, Any]]:
        """Extract device/module information from L5X"""
        devices = []

        for module in root.findall('.//Module'):
            device_data = {
                "name": module.get('Name', ''),
                "catalog_number": module.get('CatalogNumber', ''),
                "vendor": module.get('Vendor', ''),
                "product_type": module.get('ProductType', ''),
                "product_code": module.get('ProductCode', ''),
                "major_revision": module.get('Major', ''),
                "minor_revision": module.get('Minor', ''),
                "parent_module": module.get('ParentModule', ''),
                "parent_mod_port_id": module.get('ParentModPortId', ''),
                "ports": self._extract_device_ports(module)
            }
            devices.append(device_data)

        return devices

    def _get_routine_language(self, routine: ET.Element) -> str:
        """Determine routine programming language"""
        if routine.find('RLLContent') is not None:
            return "Ladder Logic"
        elif routine.find('STContent') is not None:
            return "Structured Text"
        elif routine.find('FBDContent') is not None:
            return "Function Block Diagram"
        else:
            return "Unknown"

    def _get_description(self, element: ET.Element) -> str:
        """Extract description from XML element"""
        desc_elem = element.find('Description')
        if desc_elem is not None and desc_elem.text:
            return desc_elem.text.strip()
        return ""

    def _extract_routine_parameters(self, routine: ET.Element) -> List[Dict[str, Any]]:
        """Extract routine parameters"""
        parameters = []
        # Implementation for extracting routine parameters
        # This would parse the routine's parameter structure
        return parameters

    def _extract_local_tags(self, routine: ET.Element) -> List[Dict[str, Any]]:
        """Extract local tags from routine"""
        local_tags = []
        for tag in routine.findall('.//LocalTag'):
            local_tags.append({
                "name": tag.get('Name', ''),
                "data_type": tag.get('DataType', ''),
                "dimensions": tag.get('Dimensions', ''),
                "usage": tag.get('Usage', ''),
                "description": self._get_description(tag)
            })
        return local_tags

    def _extract_aoi_parameters(self, aoi: ET.Element) -> List[Dict[str, Any]]:
        """Extract AOI parameters"""
        parameters = []
        for param in aoi.findall('.//Parameter'):
            parameters.append({
                "name": param.get('Name', ''),
                "tag_type": param.get('TagType', ''),
                "data_type": param.get('DataType', ''),
                "usage": param.get('Usage', ''),
                "required": param.get('Required', ''),
                "visible": param.get('Visible', ''),
                "description": self._get_description(param)
            })
        return parameters

    def _extract_aoi_local_tags(self, aoi: ET.Element) -> List[Dict[str, Any]]:
        """Extract AOI local tags"""
        local_tags = []
        for tag in aoi.findall('.//LocalTag'):
            local_tags.append({
                "name": tag.get('Name', ''),
                "data_type": tag.get('DataType', ''),
                "usage": tag.get('Usage', ''),
                "description": self._get_description(tag)
            })
        return local_tags

    def _extract_udt_members(self, udt: ET.Element) -> List[Dict[str, Any]]:
        """Extract UDT member information"""
        members = []
        for member in udt.findall('.//Member'):
            members.append({
                "name": member.get('Name', ''),
                "data_type": member.get('DataType', ''),
                "dimension": member.get('Dimension', ''),
                "radix": member.get('Radix', ''),
                "hidden": member.get('Hidden', ''),
                "target": member.get('Target', ''),
                "description": self._get_description(member)
            })
        return members

    def _calculate_udt_size(self, udt: ET.Element) -> int:
        """Calculate UDT size in bytes"""
        # Simplified size calculation
        members = self._extract_udt_members(udt)
        return len(members) * 4  # Rough estimate, would need proper calculation

    def _extract_device_ports(self, module: ET.Element) -> List[Dict[str, Any]]:
        """Extract device port information"""
        ports = []
        for port in module.findall('.//Port'):
            ports.append({
                "id": port.get('Id', ''),
                "type": port.get('Type', ''),
                "address": port.get('Address', ''),
                "upstream": port.get('Upstream', '')
            })
        return ports

    def _identify_document_type(self, text: str, title: str) -> str:
        """Identify document type based on content analysis"""
        text_lower = text.lower()
        title_lower = title.lower()

        if any(keyword in text_lower or keyword in title_lower for keyword in
               ['safety', 'hazard', 'risk', 'emergency']):
            return "Safety Manual"
        elif any(keyword in text_lower or keyword in title_lower for keyword in
                ['specification', 'requirement', 'design']):
            return "System Specification"
        elif any(keyword in text_lower or keyword in title_lower for keyword in
                ['manual', 'instruction', 'guide', 'procedure']):
            return "User Manual"
        elif any(keyword in text_lower or keyword in title_lower for keyword in
                ['maintenance', 'service', 'repair', 'troubleshoot']):
            return "Maintenance Manual"
        else:
            return "General Documentation"

    def _extract_sections_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract document sections based on headers"""
        sections = []
        lines = text.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Simple heuristic for section headers (all caps, or numbered)
            if (line.isupper() and len(line) > 3) or \
               (line[0].isdigit() and '.' in line[:10]):

                # Save previous section
                if current_section:
                    sections.append({
                        "title": current_section,
                        "content": '\n'.join(section_content),
                        "word_count": len(' '.join(section_content).split())
                    })

                # Start new section
                current_section = line
                section_content = []
            else:
                section_content.append(line)

        # Add final section
        if current_section:
            sections.append({
                "title": current_section,
                "content": '\n'.join(section_content),
                "word_count": len(' '.join(section_content).split())
            })

        return sections

    def _extract_qa_pairs_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential Q&A pairs from text using simple heuristics"""
        qa_pairs = []
        lines = text.split('\n')

        question_indicators = ['?', 'how to', 'what is', 'why', 'when', 'where', 'how']

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Look for questions
            if any(indicator in line_lower for indicator in question_indicators) and \
               (line.endswith('?') or any(q_word in line_lower[:20] for q_word in ['how', 'what', 'why', 'when', 'where'])):

                # Look for answer in next few lines
                answer_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not lines[j].strip().endswith('?'):
                        answer_lines.append(lines[j].strip())
                    else:
                        break

                if answer_lines:
                    qa_pairs.append({
                        "question": line.strip(),
                        "answer": ' '.join(answer_lines),
                        "confidence": 0.7,  # Basic confidence score
                        "source_line": i + 1
                    })

        return qa_pairs

def main():
    """Test the document parser"""
    parser = DocumentParser()

    # Test with sample files if they exist
    test_files = [
        "sample.pdf",
        "sample.l5x"
    ]

    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"Parsing {file_path}...")
            result = parser.parse_document(file_path)
            if result:
                print(f"Successfully parsed {file_path}")
                print(f"File type: {result.file_type}")
                print(f"Checksum: {result.checksum}")
                print(f"Content keys: {list(result.content.keys())}")
            else:
                print(f"Failed to parse {file_path}")
        else:
            print(f"Test file {file_path} not found")

if __name__ == "__main__":
    main()
