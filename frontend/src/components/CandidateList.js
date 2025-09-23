import React from 'react';
import CandidateCard from './CandidateCard';
import { Button } from './ui/button';
import { User, Edit, Trash2, Download, FileUp } from 'lucide-react';

const CandidateList = ({ 
  candidates = [], 
  candidateExtraDetails = {},
  onEdit, 
  onDelete, 
  onGenerateProfileSummary, 
  onOpenExtraDetailsDialog,
  generatingProfileSummary = {},
  searchTerm = '',
  onAddFirst 
}) => {
  if (candidates.length === 0) {
    return (
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
        {!searchTerm && onAddFirst && (
          <Button onClick={onAddFirst}>
            Add First Candidate
          </Button>
        )}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {candidates.map((candidate) => {
        // Transform candidate data for our new component
        const candidateForCard = {
          id: candidate.id,
          name: candidate.name,
          skills: candidate.skills || [],
          experience: candidate.experience,
          otherDetails: {
            ...(candidate.email && { email: candidate.email }),
            ...(candidate.phone && { phone: candidate.phone }),
            ...(candidate.education && { education: candidate.education }),
            ...(candidate.document_id || candidate.raw_text ? { resume: 'Resume uploaded' } : {}),
            ...(candidateExtraDetails[candidate.id]?.length > 0 && { 
              extraDetails: `${candidateExtraDetails[candidate.id].length} additional details` 
            }),
            createdAt: new Date(candidate.created_at).toLocaleDateString()
          }
        };

        return (
          <div key={candidate.id} className="relative">
            {/* Action buttons overlay - positioned at top right */}
            <div className="absolute top-2 right-2 z-10 flex gap-1 bg-background/90 backdrop-blur-sm rounded-md p-1 shadow-sm">
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onGenerateProfileSummary?.(candidate)}
                disabled={generatingProfileSummary[candidate.id]}
                className="h-7 w-7 p-0 text-purple-600 hover:text-purple-700 hover:bg-purple-50"
                title="Generate Profile Summary PDF"
              >
                {generatingProfileSummary[candidate.id] ? (
                  <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-purple-600"></div>
                ) : (
                  <Download className="h-3 w-3" />
                )}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onOpenExtraDetailsDialog?.(candidate)}
                className="h-7 w-7 p-0 text-green-600 hover:text-green-700 hover:bg-green-50"
                title="Upload Extra Details"
              >
                <FileUp className="h-3 w-3" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onEdit?.(candidate)}
                className="h-7 w-7 p-0 hover:bg-gray-50"
                title="Edit Candidate"
              >
                <Edit className="h-3 w-3" />
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => onDelete?.(candidate.id)}
                className="h-7 w-7 p-0 text-red-600 hover:text-red-700 hover:bg-red-50"
                title="Delete Candidate"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
            
            {/* Our new CandidateCard component */}
            <CandidateCard candidate={candidateForCard} />
          </div>
        );
      })}
    </div>
  );
};

export default CandidateList;