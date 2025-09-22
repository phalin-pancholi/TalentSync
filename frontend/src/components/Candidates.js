import React, { useState, useEffect } from 'react';
import { Plus, Edit, Trash2, User, Mail, Phone, FileText, Search, Upload, FileUp, Download } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const Candidates = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [editingCandidate, setEditingCandidate] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  // Extra details upload state
  const [showExtraDetailsDialog, setShowExtraDetailsDialog] = useState(false);
  const [extraDetailsFile, setExtraDetailsFile] = useState(null);
  const [uploadingExtraDetails, setUploadingExtraDetails] = useState(false);
  const [selectedCandidateForDetails, setSelectedCandidateForDetails] = useState(null);
  const [candidateExtraDetails, setCandidateExtraDetails] = useState({});
  
  // Profile summary generation state
  const [generatingProfileSummary, setGeneratingProfileSummary] = useState({});
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    skills: ''
  });

  useEffect(() => {
    fetchCandidates();
  }, []);

  const fetchCandidates = async () => {
    try {
      const response = await axios.get(`${API}/candidates`);
      setCandidates(response.data);
      
      // Fetch extra details for all candidates
      const extraDetailsPromises = response.data.map(async (candidate) => {
        try {
          const detailsResponse = await axios.get(`${API}/candidates/${candidate.id}/extra-details`);
          return { candidateId: candidate.id, details: detailsResponse.data };
        } catch (error) {
          console.error(`Error fetching extra details for candidate ${candidate.id}:`, error);
          return { candidateId: candidate.id, details: [] };
        }
      });
      
      const extraDetailsResults = await Promise.all(extraDetailsPromises);
      const extraDetailsMap = {};
      extraDetailsResults.forEach(result => {
        extraDetailsMap[result.candidateId] = result.details;
      });
      setCandidateExtraDetails(extraDetailsMap);
      
    } catch (error) {
      console.error('Error fetching candidates:', error);
      toast.error('Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingCandidate) {
        // Update candidate
        const updateData = {
          name: formData.name,
          email: formData.email,
          phone: formData.phone || null,
          skills: formData.skills.split(',').map(s => s.trim()).filter(s => s)
        };
        
        await axios.put(`${API}/candidates/${editingCandidate.id}`, updateData);
        toast.success('Candidate updated successfully');
      } else {
        // Create new candidate (JSON data only, no file upload)
        const candidateData = {
          name: formData.name,
          email: formData.email,
          phone: formData.phone || null,
          skills: formData.skills.split(',').map(s => s.trim()).filter(s => s)
        };
        
        await axios.post(`${API}/candidates/json`, candidateData, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
        toast.success('Candidate created successfully');
      }

      resetForm();
      fetchCandidates();
    } catch (error) {
      console.error('Error saving candidate:', error);
      toast.error(error.response?.data?.detail || 'Failed to save candidate');
    }
  };

  const handleEdit = (candidate) => {
    setEditingCandidate(candidate);
    setFormData({
      name: candidate.name,
      email: candidate.email,
      phone: candidate.phone || '',
      skills: candidate.skills.join(', ')
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (candidateId) => {
    if (window.confirm('Are you sure you want to delete this candidate?')) {
      try {
        await axios.delete(`${API}/candidates/${candidateId}`);
        toast.success('Candidate deleted successfully');
        fetchCandidates();
      } catch (error) {
        console.error('Error deleting candidate:', error);
        toast.error('Failed to delete candidate');
      }
    }
  };

  const resetForm = () => {
    setFormData({
      name: '',
      email: '',
      phone: '',
      skills: ''
    });
    setEditingCandidate(null);
    setShowCreateForm(false);
  };

  const handleDocumentUpload = async () => {
    if (!uploadFile) {
      toast.error('Please select a resume or CV file');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', uploadFile);

    try {
      const response = await axios.post(`${API}/candidates/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.duplicate) {
        toast.info('This document already exists in the system');
      } else if (response.data.parsing_failed) {
        toast.warning('Document parsing failed. Please enter candidate details manually.');
      } else if (response.data.llm_unavailable) {
        toast.warning('LLM service unavailable. Please enter candidate details manually.');
      } else if (response.data.extraction_failed) {
        toast.warning('Some candidate details could not be extracted. Please review and complete.');
      } else {
        toast.success('Candidate created successfully from document!');
      }
      
      setShowUploadDialog(false);
      setUploadFile(null);
      fetchCandidates();
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Upload failed: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleExtraDetailsUpload = async () => {
    if (!extraDetailsFile) {
      toast.error('Please select a file');
      return;
    }

    if (!selectedCandidateForDetails) {
      toast.error('No candidate selected');
      return;
    }

    setUploadingExtraDetails(true);
    const formData = new FormData();
    formData.append('file', extraDetailsFile);

    try {
      const response = await axios.post(
        `${API}/candidates/${selectedCandidateForDetails.id}/extra-details`, 
        formData, 
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      toast.success('Extra details uploaded successfully!');
      setShowExtraDetailsDialog(false);
      setExtraDetailsFile(null);
      setSelectedCandidateForDetails(null);
      
      // Refresh the extra details for this candidate
      await fetchCandidateExtraDetails(selectedCandidateForDetails.id);
      
    } catch (error) {
      console.error('Extra details upload error:', error);
      const errorMessage = error.response?.data?.detail || error.message;
      toast.error('Upload failed: ' + errorMessage);
    } finally {
      setUploadingExtraDetails(false);
    }
  };

  const fetchCandidateExtraDetails = async (candidateId) => {
    try {
      const response = await axios.get(`${API}/candidates/${candidateId}/extra-details`);
      setCandidateExtraDetails(prev => ({
        ...prev,
        [candidateId]: response.data
      }));
    } catch (error) {
      console.error('Error fetching extra details:', error);
    }
  };

  const generateProfileSummary = async (candidate) => {
    if (generatingProfileSummary[candidate.id]) {
      return; // Already generating
    }

    setGeneratingProfileSummary(prev => ({
      ...prev,
      [candidate.id]: true
    }));

    try {
      const response = await axios.post(
        `${API}/candidates/${candidate.id}/profile-summary`,
        {},
        {
          responseType: 'blob', // Important for handling PDF response
          headers: {
            'Accept': 'application/pdf'
          }
        }
      );

      // Create a blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      // Generate filename
      const candidateName = candidate.name || 'candidate';
      const sanitizedName = candidateName.replace(/[^a-zA-Z0-9]/g, '_');
      link.download = `profile_summary_${sanitizedName}_${candidate.id.slice(0, 8)}.pdf`;
      
      // Trigger download
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

      toast.success(`Profile summary generated successfully for ${candidate.name || 'candidate'}`);
    } catch (error) {
      console.error('Error generating profile summary:', error);
      
      if (error.response?.status === 404) {
        toast.error('Candidate not found');
      } else if (error.response?.status === 503) {
        toast.error('LLM service is currently unavailable. Please try again later.');
      } else if (error.response?.status === 500) {
        toast.error('Failed to generate profile summary. Please try again.');
      } else {
        toast.error('An unexpected error occurred while generating the profile summary');
      }
    } finally {
      setGeneratingProfileSummary(prev => ({
        ...prev,
        [candidate.id]: false
      }));
    }
  };

  const openExtraDetailsDialog = (candidate) => {
    setSelectedCandidateForDetails(candidate);
    setShowExtraDetailsDialog(true);
    // Fetch existing extra details for this candidate
    fetchCandidateExtraDetails(candidate.id);
  };

  const filteredCandidates = candidates.filter(candidate =>
    (candidate.name && candidate.name.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (candidate.email && candidate.email.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (candidate.skills && candidate.skills.some(skill => skill.toLowerCase().includes(searchTerm.toLowerCase())))
  );

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Candidates</h1>
        <div className="flex gap-2">
          <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" className="flex items-center gap-2">
                <Upload className="h-4 w-4" />
                Upload Resume
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Resume/CV</DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select a resume or CV file
                  </label>
                  <Input
                    type="file"
                    onChange={(e) => setUploadFile(e.target.files[0])}
                    accept=".pdf,.docx,.txt"
                    className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Supported formats: PDF, DOCX, TXT
                  </p>
                </div>
                <div className="flex gap-2">
                  <Button 
                    onClick={handleDocumentUpload} 
                    disabled={uploading || !uploadFile}
                    className="flex items-center gap-2"
                  >
                    {uploading ? 'Processing...' : 'Upload & Create Candidate'}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setShowUploadDialog(false);
                      setUploadFile(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          
          {/* Extra Details Upload Dialog */}
          <Dialog open={showExtraDetailsDialog} onOpenChange={setShowExtraDetailsDialog}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>
                  Upload Extra Details for {selectedCandidateForDetails?.name || 'Candidate'}
                </DialogTitle>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select a document with extra details
                  </label>
                  <Input
                    type="file"
                    onChange={(e) => setExtraDetailsFile(e.target.files[0])}
                    accept=".pdf,.txt"
                    className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                  />
                  <p className="text-sm text-gray-500 mt-1">
                    Supported formats: PDF, TXT (max 5MB)
                  </p>
                  <p className="text-sm text-gray-600 mt-2">
                    Upload documents containing interview feedback, new skills, work summaries, or other relevant details.
                  </p>
                </div>
                
                {/* Show existing extra details if any */}
                {candidateExtraDetails[selectedCandidateForDetails?.id]?.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-gray-700 mb-2">Existing Extra Details:</h4>
                    <div className="max-h-32 overflow-y-auto space-y-2">
                      {candidateExtraDetails[selectedCandidateForDetails?.id]?.map((detail, index) => (
                        <div key={detail.id} className="p-2 bg-gray-50 rounded text-sm">
                          <div className="flex justify-between items-start">
                            <span className="text-xs text-gray-500">
                              {detail.type && <Badge variant="outline" className="mr-2">{detail.type}</Badge>}
                              {new Date(detail.created_at).toLocaleDateString()}
                            </span>
                          </div>
                          <p className="mt-1 text-gray-700 truncate">{detail.text_content.substring(0, 100)}...</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex gap-2">
                  <Button 
                    onClick={handleExtraDetailsUpload} 
                    disabled={uploadingExtraDetails || !extraDetailsFile}
                    className="flex items-center gap-2"
                  >
                    {uploadingExtraDetails ? 'Uploading...' : 'Upload Details'}
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      setShowExtraDetailsDialog(false);
                      setExtraDetailsFile(null);
                      setSelectedCandidateForDetails(null);
                    }}
                  >
                    Cancel
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          
          <Button onClick={() => setShowCreateForm(true)} className="flex items-center gap-2">
            <Plus className="h-4 w-4" />
            Add Manually
          </Button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <Input
            type="text"
            placeholder="Search candidates by name, email, or skills..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
      </div>

      {/* Create/Edit Form */}
      {showCreateForm && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>{editingCandidate ? 'Edit Candidate' : 'Add New Candidate'}</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <Input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <Input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone
                  </label>
                  <Input
                    type="tel"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Skills (comma-separated)
                  </label>
                  <Input
                    type="text"
                    value={formData.skills}
                    onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                    placeholder="e.g., Python, React, MongoDB"
                  />
                </div>
              </div>
              <div className="flex gap-2">
                <Button type="submit">
                  {editingCandidate ? 'Update Candidate' : 'Create Candidate'}
                </Button>
                <Button type="button" variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Candidates List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCandidates.map((candidate) => (
          <Card key={candidate.id} className="hover:shadow-lg transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex justify-between items-start">
                <CardTitle className="text-lg flex items-center gap-2">
                  <User className="h-5 w-5 text-blue-600" />
                  {candidate.name || 'Unnamed Candidate'}
                </CardTitle>
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => generateProfileSummary(candidate)}
                    disabled={generatingProfileSummary[candidate.id]}
                    className="h-8 w-8 p-0 text-purple-600 hover:text-purple-700"
                    title="Generate Profile Summary PDF"
                  >
                    {generatingProfileSummary[candidate.id] ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
                    ) : (
                      <Download className="h-4 w-4" />
                    )}
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => openExtraDetailsDialog(candidate)}
                    className="h-8 w-8 p-0 text-green-600 hover:text-green-700"
                    title="Upload Extra Details"
                  >
                    <FileUp className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleEdit(candidate)}
                    className="h-8 w-8 p-0"
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleDelete(candidate.id)}
                    className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {candidate.email && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Mail className="h-4 w-4" />
                  {candidate.email}
                </div>
              )}
              {candidate.phone && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Phone className="h-4 w-4" />
                  {candidate.phone}
                </div>
              )}
              {(candidate.document_id || candidate.raw_text) && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <FileText className="h-4 w-4" />
                  Resume uploaded
                </div>
              )}
              {candidate.skills && candidate.skills.length > 0 ? (
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-2">Skills:</div>
                  <div className="flex flex-wrap gap-1">
                    {candidate.skills.map((skill, index) => (
                      <Badge key={index} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-500 italic">No skills listed</div>
              )}
              {candidate.experience && (
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">Experience:</div>
                  <div className="text-sm text-gray-600">{candidate.experience}</div>
                </div>
              )}
              {candidate.education && (
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">Education:</div>
                  <div className="text-sm text-gray-600">{candidate.education}</div>
                </div>
              )}
              
              {/* Extra Details */}
              {candidateExtraDetails[candidate.id]?.length > 0 && (
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-2">Extra Details:</div>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {candidateExtraDetails[candidate.id].slice(0, 3).map((detail, index) => (
                      <div key={detail.id} className="p-2 bg-gray-50 rounded text-xs">
                        <div className="flex justify-between items-start mb-1">
                          {detail.type && <Badge variant="outline" className="text-xs">{detail.type}</Badge>}
                          <span className="text-xs text-gray-500">
                            {new Date(detail.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-gray-700 line-clamp-2">
                          {detail.text_content.length > 100 
                            ? detail.text_content.substring(0, 100) + '...' 
                            : detail.text_content}
                        </p>
                      </div>
                    ))}
                    {candidateExtraDetails[candidate.id].length > 3 && (
                      <div className="text-xs text-gray-500 text-center">
                        +{candidateExtraDetails[candidate.id].length - 3} more details
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              <div className="text-xs text-gray-500 mt-3">
                Created: {new Date(candidate.created_at).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredCandidates.length === 0 && (
        <div className="text-center py-12">
          <User className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchTerm ? 'No candidates found' : 'No candidates yet'}
          </h3>
          <p className="text-gray-500 mb-4">
            {searchTerm 
              ? 'Try adjusting your search terms' 
              : 'Get started by adding your first candidate'
            }
          </p>
          {!searchTerm && (
            <Button onClick={() => setShowCreateForm(true)}>
              Add First Candidate
            </Button>
          )}
        </div>
      )}
    </div>
  );
};

export default Candidates;
