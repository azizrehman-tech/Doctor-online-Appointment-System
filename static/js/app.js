/**
 * Online Doctor Appointment Booking System
 * Interactive Client Logic & Booking Engine
 * Inspired by Marham.pk live search & slot reservation
 */

document.addEventListener("DOMContentLoaded", function () {
    initBookingModal();
    initPortalHandlers();
});

// Global state for booking modal
let activeBooking = {
    doctorId: null,
    doctorName: "",
    specialization: "",
    locationId: null,
    locationName: "",
    date: new Date().toISOString().split("T")[0],
    slotId: null,
    slotTime: ""
};

/**
 * Open appointment booking modal for a specific doctor
 */
function openBookingModal(doctorId, doctorName, specialty, locationId, locationName) {
    activeBooking.doctorId = doctorId;
    activeBooking.doctorName = doctorName;
    activeBooking.specialization = specialty;
    activeBooking.locationId = locationId || null;
    activeBooking.locationName = locationName || "";
    activeBooking.slotId = null;
    activeBooking.slotTime = "";

    const modal = document.getElementById("booking-modal");
    if (!modal) return;

    document.getElementById("modal-doctor-name").textContent = doctorName;
    document.getElementById("modal-specialty").textContent = specialty;
    if (document.getElementById("modal-location")) {
        document.getElementById("modal-location").textContent = locationName ? `at ${locationName}` : "";
    }

    // Set today's date in input
    const dateInput = document.getElementById("booking-date-input");
    if (dateInput) {
        dateInput.value = activeBooking.date;
        dateInput.min = new Date().toISOString().split("T")[0];
    }

    // Fetch slots for this doctor and date
    loadAvailableSlots(doctorId, activeBooking.date);

    modal.classList.add("show");
}

function closeBookingModal() {
    const modal = document.getElementById("booking-modal");
    if (modal) modal.classList.remove("show");
}

/**
 * Fetch available time slots from Flask API
 */
async function loadAvailableSlots(doctorId, dateStr) {
    const container = document.getElementById("slots-container");
    const statusText = document.getElementById("slots-status-text");
    if (!container) return;

    container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 20px; color: #64748B;">Loading available slots...</div>';
    if (statusText) statusText.textContent = "";

    try {
        const res = await fetch(`/api/doctor/${doctorId}/slots?date=${encodeURIComponent(dateStr)}`);
        const slots = await res.json();

        container.innerHTML = "";
        if (!slots || slots.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 24px; background: #F8FAFC; border-radius: 8px; border: 1px dashed #CBD5E1;">
                    <p style="color: #64748B; font-size: 0.92rem; margin-bottom: 8px;">No open time slots available on this date.</p>
                    <small style="color: #94A3B8;">Please try selecting tomorrow or another day.</small>
                </div>
            `;
            return;
        }

        slots.forEach(slot => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = `slot-item ${slot.slot_status === 'Available' ? '' : 'booked'}`;
            
            // Format time 10:00:00 -> 10:00 AM
            const startClean = slot.start_time.split(".")[0].slice(0, 5);
            btn.innerHTML = `<span>${startClean}</span><br><small style="font-size: 0.72rem; opacity: 0.8;">${slot.location_name || ''}</small>`;
            
            if (slot.slot_status === 'Available') {
                btn.onclick = () => selectSlot(slot.slot_id, `${startClean} (${slot.location_name})`, btn);
            } else {
                btn.disabled = true;
                btn.title = "Already booked";
            }
            container.appendChild(btn);
        });

    } catch (err) {
        console.error("Failed to load slots:", err);
        container.innerHTML = '<div style="color: #EF4444; text-align: center; padding: 10px;">Failed to load time slots. Please try again.</div>';
    }
}

function selectSlot(slotId, timeStr, element) {
    activeBooking.slotId = slotId;
    activeBooking.slotTime = timeStr;

    // Highlight selected slot
    document.querySelectorAll(".slot-item").forEach(el => el.classList.remove("selected"));
    element.classList.add("selected");

    const confirmBtn = document.getElementById("confirm-booking-btn");
    if (confirmBtn) {
        confirmBtn.disabled = false;
        confirmBtn.textContent = `Confirm Booking for ${timeStr}`;
    }
}

function initBookingModal() {
    const dateInput = document.getElementById("booking-date-input");
    if (dateInput) {
        dateInput.addEventListener("change", function () {
            activeBooking.date = this.value;
            if (activeBooking.doctorId) {
                loadAvailableSlots(activeBooking.doctorId, this.value);
            }
        });
    }

    const form = document.getElementById("appointment-booking-form");
    if (form) {
        form.addEventListener("submit", async function (e) {
            e.preventDefault();
            if (!activeBooking.slotId) {
                alert("Please select an available time slot first.");
                return;
            }

            const confirmBtn = document.getElementById("confirm-booking-btn");
            if (confirmBtn) {
                confirmBtn.disabled = true;
                confirmBtn.textContent = "Reserving your appointment...";
            }

            const formData = new FormData(form);
            const payload = {
                slot_id: activeBooking.slotId,
                doctor_id: activeBooking.doctorId,
                reason: formData.get("reason") || "Consultation",
                patient_name: formData.get("patient_name") || "",
                patient_email: formData.get("patient_email") || "",
                patient_phone: formData.get("patient_phone") || ""
            };

            try {
                const res = await fetch("/api/appointments/book", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const result = await res.json();

                if (result.success) {
                    showBookingSuccess(result.appointment_id);
                } else {
                    alert(result.message || "Failed to book appointment. Please try again.");
                    if (confirmBtn) confirmBtn.disabled = false;
                }
            } catch (err) {
                console.error("Booking error:", err);
                alert("Network error occurred while booking. Please try again.");
                if (confirmBtn) confirmBtn.disabled = false;
            }
        });
    }
}

function showBookingSuccess(appointmentId) {
    const body = document.getElementById("modal-booking-body");
    if (!body) return;

    body.innerHTML = `
        <div style="text-align: center; padding: 24px 10px;">
            <div style="width: 64px; height: 64px; background: #D1FAE5; color: #10B981; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 16px;">
                ✓
            </div>
            <h3 style="color: #0F172A; margin-bottom: 8px;">Appointment Confirmed!</h3>
            <p style="color: #64748B; font-size: 0.95rem; margin-bottom: 18px;">
                Your appointment with <strong>${activeBooking.doctorName}</strong> has been successfully booked.
            </p>
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-bottom: 24px; text-align: left; font-size: 0.9rem;">
                <div><strong>Appointment ID:</strong> #${appointmentId}</div>
                <div><strong>Date:</strong> ${activeBooking.date}</div>
                <div><strong>Time:</strong> ${activeBooking.slotTime}</div>
                <div><strong>Status:</strong> <span style="color: #10B981; font-weight: 600;">Confirmed</span></div>
            </div>
            <div style="display: flex; gap: 12px; justify-content: center;">
                <a href="/portal/patient" class="btn btn-primary">Go to My Appointments</a>
                <button type="button" class="btn btn-outline" onclick="closeBookingModal(); location.reload();">Close</button>
            </div>
        </div>
    `;
}

/**
 * Portal Handlers (Admin Approvals, Doctor Locations, Slot Generator)
 */
function initPortalHandlers() {
    // Admin Doctor Approval
    window.handleDoctorStatus = async function (doctorId, newStatus) {
        if (!confirm(`Are you sure you want to mark this doctor as ${newStatus}?`)) return;

        try {
            const res = await fetch(`/api/admin/doctor/${doctorId}/status`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ status: newStatus })
            });
            const data = await res.json();
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.message || "Failed to update status.");
            }
        } catch (e) {
            console.error(e);
            alert("Error updating doctor status.");
        }
    };

    // Patient Appointment Cancellation
    window.cancelAppointment = async function (appointmentId) {
        if (!confirm("Are you sure you want to cancel this appointment? Your time slot will be reopened for other patients.")) return;

        try {
            const res = await fetch(`/api/appointments/${appointmentId}/cancel`, {
                method: "POST"
            });
            const data = await res.json();
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.message || "Cancellation failed.");
            }
        } catch (e) {
            console.error(e);
            alert("Error cancelling appointment.");
        }
    };
}
