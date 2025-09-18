import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Mail, MapPin, Briefcase, Star, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Candidates = () => {
  const { id } = useParams();
  const [job, setJob] = useState(null);
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobAndCandidates();
  }, [id]);

  const fetchJobAndCandidates = async () => {
    try {
      const [jobResponse, candidatesResponse] = await Promise.all([
        axios.get(`${API}/jobs/${id}`),
        axios.get(`${API}/jobs/${id}/candidates`)
      ]);
      
      setJob(jobResponse.data);
      setCandidates(candidatesResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  };

  const getMatchColor = (percentage) => {
    if (percentage >= 80) return 'text-green-600 bg-green-100';
    if (percentage >= 60) return 'text-blue-600 bg-blue-100';
    if (percentage >= 40) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getMatchLabel = (percentage) => {
    if (percentage >= 80) return 'Excellent Match';
    if (percentage >= 60) return 'Good Match';
    if (percentage >= 40) return 'Fair Match';
    return 'Limited Match';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-4 mb-2">
            <Link to={`/jobs/${id}`}>
              <Button variant="outline" size="sm" className="btn-animate">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Job
              </Button>
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-slate-800">Candidate Matches</h1>
          <p className="text-slate-600 mt-1">
            {job?.title && `Candidates for "${job.title}"`}
          </p>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-slate-600">
          <div className="flex items-center space-x-2">
            <TrendingUp className="w-4 h-4" />
            <span>{candidates.length} candidates found</span>
          </div>
        </div>
      </div>

      {/* Job Summary Card */}
      {job && (
        <Card className="card-hover animate-slide-up">
          <CardHeader>
            <CardTitle className="text-lg">{job.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-4">
              {job.skills.map((skill, index) => (
                <Badge key={index} variant="outline" className="skill-badge">
                  {skill}
                </Badge>
              ))}
            </div>
            <div className="flex flex-wrap items-center gap-4 text-sm text-slate-600">
              <span>{job.department}</span>
              <span>•</span>
              <span>{job.location}</span>
              <span>•</span>
              <span>{job.experience_level} Level</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Candidates List */}
      {candidates.length === 0 ? (
        <div className="text-center py-12">
          <User className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-slate-600 mb-2">No candidates found</h3>
          <p className="text-slate-500">No matching candidates for this position</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {candidates.map((candidate) => (
            <Card key={candidate.id} className="card-hover animate-slide-up">
              <CardHeader className="pb-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold text-slate-800 flex items-center space-x-2">
                      <User className="w-5 h-5 text-blue-600" />
                      <span>{candidate.name}</span>
                    </CardTitle>
                    <p className="text-slate-600 mt-1">{candidate.current_role}</p>
                  </div>
                  
                  <div className="text-right">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getMatchColor(candidate.match_percentage)}`}>
                      <Star className="w-3 h-3 mr-1" />
                      {candidate.match_percentage}%
                    </div>
                    <p className="text-xs text-slate-500 mt-1">
                      {getMatchLabel(candidate.match_percentage)}
                    </p>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Contact Info */}
                <div className="flex items-center space-x-4 text-sm text-slate-600">
                  <div className="flex items-center space-x-1">
                    <Mail className="w-3 h-3" />
                    <span>{candidate.email}</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <MapPin className="w-3 h-3" />
                    <span>{candidate.location}</span>
                  </div>
                </div>

                {/* Experience and Department */}
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1 text-slate-600">
                    <Briefcase className="w-3 h-3" />
                    <span>{candidate.experience_years} years experience</span>
                  </div>
                  <Badge variant="secondary" className="text-xs">
                    {candidate.department}
                  </Badge>
                </div>

                {/* Match Progress */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-slate-700">Skill Match</span>
                    <span className="text-sm text-slate-600">
                      {candidate.matched_skills.length} of {job?.skills.length || 0} skills
                    </span>
                  </div>
                  <Progress 
                    value={candidate.match_percentage} 
                    className="h-2 progress-animated"
                    style={{'--progress-width': `${candidate.match_percentage}%`}}
                  />
                </div>

                {/* Matched Skills */}
                <div>
                  <p className="text-sm font-medium text-slate-700 mb-2">Matched Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {candidate.matched_skills.length > 0 ? (
                      candidate.matched_skills.map((skill, index) => (
                        <Badge key={index} variant="default" className="text-xs bg-green-100 text-green-800 border-green-200">
                          {skill}
                        </Badge>
                      ))
                    ) : (
                      <span className="text-sm text-slate-500">No matching skills</span>
                    )}
                  </div>
                </div>

                {/* All Skills */}
                <div>
                  <p className="text-sm font-medium text-slate-700 mb-2">All Skills</p>
                  <div className="flex flex-wrap gap-1">
                    {candidate.skills.map((skill, index) => {
                      const isMatched = candidate.matched_skills.includes(skill);
                      return (
                        <Badge 
                          key={index} 
                          variant="outline" 
                          className={`text-xs ${isMatched ? 'bg-green-50 border-green-200 text-green-700' : 'skill-badge'}`}
                        >
                          {skill}
                        </Badge>
                      );
                    })}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex space-x-2 pt-4 border-t border-slate-100">
                  <Button 
                    size="sm" 
                    className="flex-1 btn-animate gradient-teal-blue text-white"
                    onClick={() => toast.success(`Contacted ${candidate.name}`)}
                  >
                    Contact Candidate
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="btn-animate"
                    onClick={() => toast.success(`Added ${candidate.name} to shortlist`)}
                  >
                    Shortlist
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default Candidates;