import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

interface Task {
    id: number;
    title: string;
    description: string;
    status: string;
    deadline: string;
}

interface Activity {
    id: number;
    name: string;
    purpose: string;
}

const containerVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            duration: 0.6,
            staggerChildren: 0.1
        }
    }
};

const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: {
        opacity: 1,
        x: 0,
        transition: { duration: 0.4 }
    }
};

const Dashboard: React.FC = () => {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = React.useState('overview');
    const [tasks, setTasks] = React.useState<Task[]>([]);
    const [activities, setActivities] = React.useState<Activity[]>([]);

    React.useEffect(() => {
        // Fetch tasks and activities from API
        fetch('/api/tasks')
            .then(res => res.json())
            .then(data => setTasks(data));
    }, []);

    return (
        <motion.div
            className="container"
            initial="hidden"
            animate="visible"
            variants={containerVariants}
        >
            <div className="header">
                <motion.h1
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    Dashboard
                </motion.h1>
                <div className="user-info">
                    <span>Organization Name</span>
                    <motion.button
                        className="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => navigate('/logout')}
                    >
                        Logout
                    </motion.button>
                </div>
            </div>

            <motion.div className="overview" variants={containerVariants}>
                <motion.div className="stat-card" variants={itemVariants}>
                    <h3>Compliance Score</h3>
                    <motion.div
                        className="value"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                    >
                        85%
                    </motion.div>
                    <div className="change">↑ 5% this month</div>
                </motion.div>

                <motion.div className="stat-card" variants={itemVariants}>
                    <h3>Active Tasks</h3>
                    <motion.div
                        className="value"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.6, delay: 0.3 }}
                    >
                        {tasks.length}
                    </motion.div>
                    <div className="change">2 due this week</div>
                </motion.div>

                <motion.div className="stat-card" variants={itemVariants}>
                    <h3>Data Processing Activities</h3>
                    <motion.div
                        className="value"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                    >
                        {activities.length}
                    </motion.div>
                    <div className="change">Updated today</div>
                </motion.div>
            </motion.div>

            <motion.div className="nav-tabs" variants={containerVariants}>
                {['Overview', 'Tasks', 'Activities', 'Documents'].map((tab, index) => (
                    <motion.div
                        key={tab}
                        className={`nav-tab ${activeTab === tab.toLowerCase() ? 'active' : ''}`}
                        variants={itemVariants}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setActiveTab(tab.toLowerCase())}
                    >
                        {tab}
                    </motion.div>
                ))}
            </motion.div>

            <motion.div className="tasks-section" variants={containerVariants}>
                <div className="section-header">
                    <h2>Compliance Tasks</h2>
                    <motion.button
                        className="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        Add Task
                    </motion.button>
                </div>
                <motion.div className="task-list" variants={containerVariants}>
                    {tasks.map((task) => (
                        <motion.div
                            key={task.id}
                            className="task-item"
                            variants={itemVariants}
                            whileHover={{ scale: 1.02 }}
                        >
                            <div>
                                <h3>{task.title}</h3>
                                <p>{task.deadline}</p>
                            </div>
                            <span className={`status ${task.status}`}>
                                {task.status}
                            </span>
                        </motion.div>
                    ))}
                </motion.div>
            </motion.div>

            <motion.div className="activities-section" variants={containerVariants}>
                <div className="section-header">
                    <h2>Data Processing Activities</h2>
                    <motion.button
                        className="button"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        Add Activity
                    </motion.button>
                </div>
                <motion.div className="activity-list" variants={containerVariants}>
                    {activities.map((activity) => (
                        <motion.div
                            key={activity.id}
                            className="activity-item"
                            variants={itemVariants}
                            whileHover={{ scale: 1.02 }}
                        >
                            <div>
                                <h3>{activity.name}</h3>
                                <p>{activity.purpose}</p>
                            </div>
                            <motion.button
                                className="button"
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                            >
                                View Details
                            </motion.button>
                        </motion.div>
                    ))}
                </motion.div>
            </motion.div>
        </motion.div>
    );
};

export default Dashboard; 