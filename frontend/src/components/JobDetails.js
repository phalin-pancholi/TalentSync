import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { Edit, Trash2, Users, MapPin, Clock, Briefcase, Tag } from 'lucide-react';
import { Button } from './ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from './ui/dialog';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Badge } from './ui/badge';
import { toast } from 'sonner';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

const JobDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    skills: '',
    experience_level: '',
    department: '',
    location: ''
  });

  useEffect(() => {
    fetchJob();
  }, [id]);

  const fetchJob = async () => {
    try {
      const response = await axios.get(`${API}/jobs/${id}`);
      const jobData = response.data;
      setJob(jobData);
      setFormData({
        title: jobData.title,
        description: jobData.description,
        skills: jobData.skills.join(', '),
        experience_level: jobData.experience_level,
        department: jobData.department,
        location: jobData.location
      });
    } catch (error) {
      console.error('Error fetching job:', error);
      toast.error('Failed to fetch job details');
      navigate('/');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateJob = async (e) => {
    e.preventDefault();
    
    try {
      const updateData = {
        ...formData,
        skills: formData.skills.split(',').map(skill => skill.trim()).filter(skill => skill)
      };

      await axios.put(`${API}/jobs/${id}`, updateData);
      toast.success('Job posting updated successfully!');
      setShowEditDialog(false);
      fetchJob();
    } catch (error) {
      console.error('Error updating job:', error);
      toast.error('Failed to update job posting');
    }
  };

  const handleDeleteJob = async () => {
    try {
      await axios.delete(`${API}/jobs/${id}`);
      toast.success('Job posting deleted successfully!');
      navigate('/');
    } catch (error) {
      console.error('Error deleting job:', error);
      toast.error('Failed to delete job posting');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <Briefcase className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-slate-600 mb-2">Job not found</h3>
        <p className="text-slate-500">The job posting you're looking for doesn't exist.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-3xl font-bold text-slate-800">{job.title}</h1>
            <Badge variant="secondary" className="text-sm">
              {job.experience_level}
            </Badge>
          </div>
          
          <div className="flex flex-wrap items-center gap-4 text-slate-600">
            <div className="flex items-center space-x-1">
              <MapPin className="w-4 h-4" />
              <span>{job.location}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Briefcase className="w-4 h-4" />
              <span>{job.department}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Clock className="w-4 h-4" />
              <span>Posted {formatDate(job.created_at)}</span>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-3">
          <Link to={`/jobs/${job.id}/candidates`}>
            <Button className="btn-animate gradient-teal-blue text-white">
              <Users className="w-4 h-4 mr-2" />
              View Candidates
            </Button>
          </Link>
          
          {/* Edit Job Dialog */}
          <Dialog open={showEditDialog} onOpenChange={setShowEditDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" className="btn-animate">
                <Edit className="w-4 h-4 mr-2" />
                Edit Job
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-2xl">
              <DialogHeader>
                <DialogTitle>Edit Job Posting</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleUpdateJob} className="space-y-4">
                <Input
                  placeholder="Job Title"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  required
                />
                <Textarea
                  placeholder="Job Description"
                  rows={4}
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                  required
                />
                <Input
                  placeholder="Required Skills (comma-separated)"
                  value={formData.skills}
                  onChange={(e) => setFormData({...formData, skills: e.target.value})}
                  required
                />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Select value={formData.experience_level} onValueChange={(value) => setFormData({...formData, experience_level: value})}>
                    <SelectTrigger>
                      <SelectValue placeholder="Experience Level" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Entry">Entry Level</SelectItem>
                      <SelectItem value="Mid">Mid Level</SelectItem>
                      <SelectItem value="Senior">Senior Level</SelectItem>
                      <SelectItem value="Lead">Lead Level</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input
                    placeholder="Department"
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    required
                  />
                </div>
                <Input
                  placeholder="Location"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  required
                />
                <Button type="submit" className="w-full btn-animate gradient-green-teal text-white">
                  Update Job Posting
                </Button>
              </form>
            </DialogContent>
          </Dialog>

          {/* Delete Job Dialog */}
          <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
            <DialogTrigger asChild>
              <Button variant="outline" className="btn-animate text-red-600 border-red-200 hover:bg-red-50">
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Job
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Delete Job Posting</DialogTitle>
              </DialogHeader>
              <p className="text-slate-600">
                Are you sure you want to delete this job posting? This action cannot be undone.
              </p>
              <DialogFooter className="space-x-2">
                <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
                  Cancel
                </Button>
                <Button 
                  onClick={handleDeleteJob}
                  className="bg-red-600 hover:bg-red-700 text-white"
                >
                  Delete Job
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Job Details Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Job Information */}
        <div className="lg:col-span-2">
          <Card className="card-hover animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Briefcase className="w-5 h-5 text-blue-600" />
                <span>Job Description</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="prose prose-slate max-w-none">
                <p className="text-slate-700 leading-relaxed whitespace-pre-line">
                  {job.description}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar Information */}
        <div className="space-y-6">
          {/* Required Skills */}
          <Card className="card-hover animate-slide-up">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Tag className="w-5 h-5 text-green-600" />
                <span>Required Skills</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {job.skills.map((skill, index) => (
                  <Badge key={index} variant="outline" className="skill-badge">
                    {skill}
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Job Details Summary */}
          <Card className="card-hover animate-slide-up">
            <CardHeader>
              <CardTitle>Job Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-slate-600 font-medium">Department</span>
                <span className="text-slate-800">{job.department}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-slate-600 font-medium">Location</span>
                <span className="text-slate-800">{job.location}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-slate-600 font-medium">Experience</span>
                <span className="text-slate-800">{job.experience_level}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-slate-600 font-medium">Last Updated</span>
                <span className="text-slate-800 text-sm">
                  {formatDate(job.updated_at)}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="card-hover animate-slide-up">
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Link to={`/jobs/${job.id}/candidates`} className="block">
                <Button className="w-full btn-animate gradient-teal-blue text-white">
                  <Users className="w-4 h-4 mr-2" />
                  Find Candidates
                </Button>
              </Link>
              <Button 
                variant="outline" 
                className="w-full btn-animate"
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  toast.success('Job link copied to clipboard!');
                }}
              >
                Share Job Link
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default JobDetails;