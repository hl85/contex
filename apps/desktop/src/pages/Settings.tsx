import { useState, useEffect } from 'react';
import Form from '@rjsf/core';
import validator from '@rjsf/validator-ajv8';
import { useNavigate } from 'react-router-dom';

const API_URL = "http://127.0.0.1:12345";

interface SkillManifest {
    id: string;
    name: string;
    description: string;
    config_schema: any;
}

export default function Settings() {
    const navigate = useNavigate();
    const [skills, setSkills] = useState<SkillManifest[]>([]);
    const [selectedSkill, setSelectedSkill] = useState<SkillManifest | null>(null);
    const [formData, setFormData] = useState<any>({});
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");

    // Fetch Skills
    useEffect(() => {
        fetch(`${API_URL}/skills`)
            .then(res => res.json())
            .then(data => {
                setSkills(data);
                if (data.length > 0) {
                    setSelectedSkill(data[0]);
                }
            })
            .catch(err => console.error("Failed to fetch skills", err));
    }, []);

    // Fetch Config when skill changes
    useEffect(() => {
        if (!selectedSkill) return;

        setLoading(true);
        fetch(`${API_URL}/config/${selectedSkill.id}`)
            .then(res => res.json())
            .then(data => {
                // If data is empty, we might want to use defaults from schema
                // But RJSF handles defaults if we don't pass formData? 
                // Actually better to pass what we have.
                setFormData(data || {});
            })
            .catch(err => console.error("Failed to fetch config", err))
            .finally(() => setLoading(false));
    }, [selectedSkill]);

    const handleSubmit = async ({ formData }: any) => {
        if (!selectedSkill) return;
        setStatus("Saving...");
        try {
            const res = await fetch(`${API_URL}/config/${selectedSkill.id}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ config: formData }),
            });
            if (res.ok) {
                setStatus("Saved successfully!");
                setFormData(formData); // Update local state
                setTimeout(() => setStatus(""), 2000);
            } else {
                setStatus("Failed to save.");
            }
        } catch (e) {
            console.error(e);
            setStatus("Error saving.");
        }
    };

    return (
        <div className="container" style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
            <header className="header" style={{ marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button onClick={() => navigate("/")} className="action-btn">
                    &larr; Back to Dashboard
                </button>
                <h1>Settings</h1>
            </header>

            <div style={{ display: 'flex', gap: '20px', minHeight: '400px' }}>
                {/* Sidebar */}
                <div style={{ width: '200px', borderRight: '1px solid #333' }}>
                    <h3>Skills</h3>
                    <ul style={{ listStyle: 'none', padding: 0 }}>
                        {skills.map(skill => (
                            <li key={skill.id} style={{ marginBottom: '10px' }}>
                                <button 
                                    onClick={() => setSelectedSkill(skill)}
                                    style={{ 
                                        width: '100%', 
                                        textAlign: 'left',
                                        background: selectedSkill?.id === skill.id ? '#334155' : 'transparent',
                                        border: 'none',
                                        color: 'white',
                                        padding: '8px',
                                        cursor: 'pointer',
                                        borderRadius: '4px'
                                    }}
                                >
                                    {skill.name}
                                </button>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* Main Content */}
                <div style={{ flex: 1 }}>
                    {selectedSkill ? (
                        <>
                            <h2>{selectedSkill.name}</h2>
                            <p style={{ color: '#aaa', marginBottom: '20px' }}>{selectedSkill.description}</p>
                            
                            {loading ? (
                                <p>Loading config...</p>
                            ) : (
                                <div className="rjsf-dark-theme">
                                    <Form
                                        schema={selectedSkill.config_schema}
                                        formData={formData}
                                        validator={validator}
                                        onChange={e => setFormData(e.formData)}
                                        onSubmit={handleSubmit}
                                    >
                                        <div style={{ marginTop: '20px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                                            <button type="submit" className="primary-btn">Save Configuration</button>
                                            {status && <span style={{ color: '#4ade80' }}>{status}</span>}
                                        </div>
                                    </Form>
                                </div>
                            )}
                        </>
                    ) : (
                        <p>No skills found.</p>
                    )}
                </div>
            </div>
        </div>
    );
}
