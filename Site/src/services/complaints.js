import API from './api';

export const createComplaint = (listingId, complaintTypeId, description = '') =>
    API.post(`/complaints/${listingId}`, {
        complaint_type_id: complaintTypeId,
        description
    }).then(r => r.data);