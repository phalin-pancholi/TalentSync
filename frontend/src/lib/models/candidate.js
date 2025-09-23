/**
 * Candidate model for representing individual candidates
 */
export class Candidate {
  constructor({ id, name, skills = [], experience = '', ...otherDetails } = {}) {
    this.id = id;
    this.name = name;
    this.skills = Array.isArray(skills) ? skills : [];
    this.experience = experience;
    this.otherDetails = otherDetails;
  }

  /**
   * Get minimal details for card display
   * @returns {Object} Object with name, skills, and experience
   */
  getMinimalDetails() {
    return {
      name: this.name || 'Unknown',
      skills: this.skills,
      experience: this.experience
    };
  }

  /**
   * Get all candidate details
   * @returns {Object} Complete candidate object
   */
  getAllDetails() {
    return {
      id: this.id,
      name: this.name,
      skills: this.skills,
      experience: this.experience,
      ...this.otherDetails
    };
  }

  /**
   * Validate if candidate has required fields
   * @returns {boolean} True if valid
   */
  isValid() {
    return Boolean(this.id && this.name);
  }
}

export default Candidate;