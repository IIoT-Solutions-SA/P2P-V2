import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ComingSoonModal } from '../components/ui/ComingSoonModal';
// import { API_BASE_URL } from '../config/environment'; // Will be used when Connect feature is enabled
import './Connect.css';

interface Member {
  id: string;
  email: string;
  name: string;
  company?: string;
  title?: string;
  location?: string;
  industrySector?: string;
  expertiseTags?: string[];
  role: string;
}

export default function Connect() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [members] = useState<Member[]>([]); // Will be populated when Connect feature is enabled
  const [filteredMembers, setFilteredMembers] = useState<Member[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading] = useState(true); // Will be managed when Connect feature is enabled
  const [error] = useState<string | null>(null); // Will be managed when Connect feature is enabled
  const [showComingSoon, setShowComingSoon] = useState(false);

  useEffect(() => {
    // If user is admin, redirect to user management
    if (user?.role === 'admin') {
      navigate('/user-management');
      return;
    }

    // Show coming soon modal for members
    setShowComingSoon(true);
  }, [user, navigate]);

  useEffect(() => {
    // Filter members based on search term
    if (searchTerm) {
      const filtered = members.filter(member => {
        const searchLower = searchTerm.toLowerCase();
        return (
          member.name?.toLowerCase().includes(searchLower) ||
          member.company?.toLowerCase().includes(searchLower) ||
          member.title?.toLowerCase().includes(searchLower) ||
          member.industrySector?.toLowerCase().includes(searchLower) ||
          member.expertiseTags?.some(tag => 
            tag.toLowerCase().includes(searchLower)
          )
        );
      });
      setFilteredMembers(filtered);
    } else {
      setFilteredMembers(members);
    }
  }, [searchTerm, members]);

  // Commenting out fetchMembers as it's not currently used due to coming soon feature
  // Will be enabled when Connect feature is implemented
  /*
  const fetchMembers = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/users`, {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch members');
      }
      
      const data = await response.json();
      setMembers(data.users || []);
      setFilteredMembers(data.users || []);
    } catch (err) {
      setError('Failed to load members. Please try again later.');
      console.error('Error fetching members:', err);
    } finally {
      setLoading(false);
    }
  };
  */

  const handleConnect = (memberId: string) => {
    // Future feature: Send connection request
    console.log('Connect with member:', memberId);
    alert('Connection feature coming soon!');
  };

  const handleMessage = (memberId: string) => {
    // Future feature: Send message
    console.log('Message member:', memberId);
    alert('Messaging feature coming soon!');
  };

  if (loading) {
    return (
      <div className="connect-container">
        <div className="loading">Loading members...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="connect-container">
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="connect-container">
      <div className="connect-header">
        <h1>Connect with Members</h1>
        <p>Browse and connect with other manufacturing professionals</p>
      </div>

      <div className="search-section">
        <input
          type="text"
          className="search-input"
          placeholder="Search by name, company, title, industry, or expertise..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <div className="search-stats">
          Found {filteredMembers.length} member{filteredMembers.length !== 1 ? 's' : ''}
        </div>
      </div>

      <div className="members-grid">
        {filteredMembers.map((member) => (
          <div key={member.id} className="member-card">
            <div className="member-avatar">
              {member.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            
            <div className="member-info">
              <h3>{member.name || 'Unknown User'}</h3>
              {member.title && <p className="member-title">{member.title}</p>}
              {member.company && <p className="member-company">{member.company}</p>}
              
              {member.industrySector && (
                <p className="member-industry">
                  <span className="icon">🏭</span> {member.industrySector}
                </p>
              )}
              
              {member.location && (
                <p className="member-location">
                  <span className="icon">📍</span> {member.location}
                </p>
              )}
              
              {member.expertiseTags && member.expertiseTags.length > 0 && (
                <div className="expertise-tags">
                  {member.expertiseTags.slice(0, 3).map((tag, index) => (
                    <span key={index} className="expertise-tag">{tag}</span>
                  ))}
                  {member.expertiseTags.length > 3 && (
                    <span className="expertise-tag">+{member.expertiseTags.length - 3}</span>
                  )}
                </div>
              )}
              
              <div className="member-role">
                <span className={`role-badge ${member.role}`}>
                  {member.role}
                </span>
              </div>
            </div>
            
            <div className="member-actions">
              <button 
                className="btn-message"
                onClick={() => handleMessage(member.id)}
              >
                Message
              </button>
              <button 
                className="btn-connect"
                onClick={() => handleConnect(member.id)}
              >
                Connect
              </button>
            </div>
          </div>
        ))}
      </div>

      {filteredMembers.length === 0 && (
        <div className="no-results">
          <p>No members found matching your search.</p>
          {searchTerm && (
            <button
              className="btn-clear-search"
              onClick={() => setSearchTerm('')}
            >
              Clear Search
            </button>
          )}
        </div>
      )}

      {/* Coming Soon Modal */}
      <ComingSoonModal
        isOpen={showComingSoon}
        onClose={() => {
          setShowComingSoon(false);
          navigate('/dashboard');
        }}
        featureName="Connect with Members"
        description="This feature will allow you to browse and connect with other professionals in your organization."
      />
    </div>
  );
}