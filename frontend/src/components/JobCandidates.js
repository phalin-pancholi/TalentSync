import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, User, Mail, MapPin, Briefcase, Star, TrendingUp } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const JobCandidates = () => {
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
    return 'Poor Match';
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Job not found</h2>
          <Link to="/">
            <Button>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Jobs
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <Link to={`/jobs/${id}`}>
            <Button variant="outline" size="sm">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Job
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{job.title}</h1>
            <p className="text-gray-600">Candidate Matches</p>
          </div>
        </div>
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <TrendingUp className="w-4 h-4" />
          <span>{candidates.length} candidates found</span>
        </div>
      </div>

      {/* Job Summary */}
      <Card className="mb-6 bg-blue-50 border-blue-200">
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <Briefcase className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">Department: {job.department}</span>
            </div>
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">Location: {job.location}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Star className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">Experience: {job.experience_level}</span>
            </div>
          </div>
          <div className="mt-3">
            <span className="text-sm font-medium text-gray-700">Required Skills: </span>
            <div className="flex flex-wrap gap-1 mt-1">
              {job.skills.map((skill, index) => (
                <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Candidates List */}
      {candidates.length === 0 ? (
        <div className="text-center py-12">
          <User className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No candidates found</h3>
          <p className="text-gray-600 mb-6">
            There are no candidates that match the requirements for this position.
          </p>
          <Link to="/candidates">
            <Button>
              View All Candidates
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {candidates.map((candidate) => (
            <Card key={candidate.id} className="hover:shadow-lg transition-shadow duration-200">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="text-lg flex items-center space-x-2">
                      <User className="w-5 h-5 text-blue-600" />
                      <span>{candidate.name}</span>
                    </CardTitle>
                    <p className="text-sm text-gray-600 mt-1">{candidate.current_role}</p>
                  </div>
                  <div className="text-right">
                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${getMatchColor(candidate.match_percentage)}`}>
                      {candidate.match_percentage}% Match
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{getMatchLabel(candidate.match_percentage)}</p>
                  </div>
                </div>
              </CardHeader>
              
              <CardContent className="space-y-4">
                {/* Contact Info */}
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Mail className="w-4 h-4" />
                    <span>{candidate.email}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <MapPin className="w-4 h-4" />
                    <span>{candidate.location}</span>
                  </div>
                  {/* <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <Briefcase className="w-4 h-4" />
                    <span>{candidate.experience_years} years experience</span>
                  </div> */}
                </div>

                {/* Match Progress */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-700">Skill Match</span>
                    <span className="text-sm text-gray-600">
                      {candidate.matched_skills.length} of {job.skills.length} skills
                    </span>
                  </div>
                  <Progress value={candidate.match_percentage} className="h-2" />
                </div>

                {/* Skills */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Skills</h4>
                  <div className="flex flex-wrap gap-1">
                    {candidate.skills.map((skill, index) => {
                      const isMatched = candidate.matched_skills.includes(skill);
                      return (
                        <Badge 
                          key={index} 
                          variant={isMatched ? "default" : "secondary"}
                          className={isMatched ? "bg-green-100 text-green-800" : ""}
                        >
                          {skill}
                          {isMatched && <span className="ml-1">✓</span>}
                        </Badge>
                      );
                    })}
                  </div>
                </div>

                {/* Matched Skills Highlight */}
                {candidate.matched_skills.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium text-green-700 mb-2">Matching Skills</h4>
                    <div className="flex flex-wrap gap-1">
                      {candidate.matched_skills.map((skill, index) => (
                        <Badge key={index} className="bg-green-100 text-green-800">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default JobCandidates;