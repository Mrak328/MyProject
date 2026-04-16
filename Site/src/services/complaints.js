import API from './api';

export const createComplaint = async (listingId, complaintType, description = '') => {
    const response = await API.post(`/complaints/${listingId}`, {
        complaint_type: complaintType,
        description
    });
    return response.data;
};