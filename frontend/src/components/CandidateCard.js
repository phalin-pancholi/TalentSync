import React from 'react';
import { Eye, User, Mail, Phone, Briefcase, GraduationCap, Calendar, FileText, MapPin } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const CandidateCard = ({ candidate }) => {
  if (!candidate) {
    return (
      <div className="bg-card border border-border rounded-lg p-4 shadow-sm">
        <p className="text-muted-foreground">No candidate data available</p>
      </div>
    );
  }

  const { name, skills = [], experience, location } = candidate;
  const hasOtherDetails = candidate.otherDetails && Object.keys(candidate.otherDetails).length > 0;

  // Helper function to truncate long skill lists
  const renderSkills = (skillsList, isMinimal = true) => {
    if (!skillsList || skillsList.length === 0) {
      return <span className="text-muted-foreground italic">No skills listed</span>;
    }

    if (isMinimal && skillsList.length > 3) {
      const displayedSkills = skillsList.slice(0, 3).join(', ');
      return (
        <span>
          {displayedSkills}
          <span className="text-muted-foreground">… (+{skillsList.length - 3} more)</span>
        </span>
      );
    }

    return skillsList.join(', ');
  };

  const renderExperience = (exp) => {
    if (!exp || exp === '') {
      return <span className="text-muted-foreground italic">Not provided</span>;
    }
    return exp;
  };

  const renderLocation = (loc) => {
    if (!loc || loc === '') {
      return <span className="text-muted-foreground italic">Not provided</span>;
    }
    return loc;
  };

  const renderAllSkills = (skillsList) => {
    if (!skillsList || skillsList.length === 0) {
      return <span className="text-muted-foreground italic">No skills listed</span>;
    }
    return (
      <div className="flex flex-wrap gap-2">
        {skillsList.map((skill, index) => (
          <Badge key={index} variant="secondary" className="text-xs">
            {skill}
          </Badge>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-card border border-border rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow">
      {/* Minimal Details - Always Visible */}
      <div className="space-y-3">
        {/* Header with name and action button */}
        <div className="flex items-start justify-between pr-32"> {/* Right padding for action buttons */}
          <h3 className="text-lg font-semibold text-foreground">{name || 'Unknown'}</h3>
        </div>

        <div className="space-y-2">
          <div>
            <span className="text-sm font-medium text-muted-foreground">Skills: </span>
            <span className="text-sm text-foreground">
              {renderSkills(skills, true)}
            </span>
          </div>
          
          <div>
            <span className="text-sm font-medium text-muted-foreground">Experience: </span>
            <span className="text-sm text-foreground">
              {renderExperience(experience)}
            </span>
          </div>

          <div>
            <span className="text-sm font-medium text-muted-foreground">Location: </span>
            <span className="text-sm text-foreground">
              {renderLocation(location)}
            </span>
          </div>
        </div>

        {/* Show All Details Modal Button */}
        <div className="pt-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <Eye className="w-4 h-4" />
                Show all details
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  {name || 'Unknown Candidate'}
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-6 mt-4">
                {/* Basic Information */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-4">
                    <div>
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <Briefcase className="w-4 h-4" />
                        Skills
                      </h4>
                      {renderAllSkills(skills)}
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        Experience
                      </h4>
                      <p className="text-sm text-foreground">
                        {renderExperience(experience)}
                      </p>
                    </div>

                    <div>
                      <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                        <MapPin className="w-4 h-4" />
                        Location
                      </h4>
                      <p className="text-sm text-foreground">
                        {renderLocation(location)}
                      </p>
                    </div>
                  </div>

                  {/* Contact & Additional Info */}
                  {hasOtherDetails && (
                    <div className="space-y-4">
                      {candidate.otherDetails.email && (
                        <div>
                          <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                            <Mail className="w-4 h-4" />
                            Email
                          </h4>
                          <p className="text-sm text-foreground">{candidate.otherDetails.email}</p>
                        </div>
                      )}
                      
                      {candidate.otherDetails.phone && (
                        <div>
                          <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                            <Phone className="w-4 h-4" />
                            Phone
                          </h4>
                          <p className="text-sm text-foreground">{candidate.otherDetails.phone}</p>
                        </div>
                      )}
                      
                      {candidate.otherDetails.education && (
                        <div>
                          <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                            <GraduationCap className="w-4 h-4" />
                            Education
                          </h4>
                          <p className="text-sm text-foreground">{candidate.otherDetails.education}</p>
                        </div>
                      )}
                      
                      {candidate.otherDetails.resume && (
                        <div>
                          <h4 className="font-semibold text-foreground mb-2 flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            Resume
                          </h4>
                          <p className="text-sm text-foreground">{candidate.otherDetails.resume}</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Additional Details */}
                {hasOtherDetails && (
                  <div className="border-t pt-4">
                    <h4 className="font-semibold text-foreground mb-3">Additional Information</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {Object.entries(candidate.otherDetails || {})
                        .filter(([key]) => !['email', 'phone', 'education', 'resume'].includes(key))
                        .map(([key, value]) => (
                          <div key={key}>
                            <h5 className="text-sm font-medium text-muted-foreground capitalize mb-1">
                              {key.replace(/([A-Z])/g, ' $1').trim()}
                            </h5>
                            <p className="text-sm text-foreground">
                              {Array.isArray(value) ? value.join(', ') : String(value)}
                            </p>
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    </div>
  );
};

export default CandidateCard;