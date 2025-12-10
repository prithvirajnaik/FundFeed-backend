from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import models
from django.utils import timezone
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from .models import ContactRequest
from .serializers import ContactRequestSerializer, ContactRequestCreateSerializer
from pitches.models import Pitch
from investor_posts.models import InvestorPost

class ContactRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ContactRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # Base query: requests involving the user
        queryset = ContactRequest.objects.filter(
            models.Q(developer=user) | models.Q(investor=user)
        )

        # Only apply inbox/sent filtering for list actions
        # For retrieve/update/delete, just return all requests involving the user
        if self.action == 'list':
            box = self.request.query_params.get("box", "inbox")
            
            if box == "sent":
                # User is SENDER if:
                # 1. They are Investor AND request is about a Pitch
                # 2. They are Developer AND request is about an InvestorPost
                queryset = queryset.filter(
                    models.Q(investor=user, pitch__isnull=False) |
                    models.Q(developer=user, investor_post__isnull=False)
                )
            else:
                # Default: INBOX (User is RECEIVER)
                # User is RECEIVER if:
                # 1. They are Developer AND request is about a Pitch
                # 2. They are Investor AND request is about an InvestorPost
                queryset = queryset.filter(
                    models.Q(developer=user, pitch__isnull=False) |
                    models.Q(investor=user, investor_post__isnull=False)
                )

        return queryset.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "create":
            return ContactRequestCreateSerializer
        return ContactRequestSerializer

    def perform_create(self, serializer):
        # Logic to determine sender and receiver
        # If sender is Investor -> Receiver is Developer (from Pitch)
        # If sender is Developer -> Receiver is Investor (from InvestorPost)
        
        user = self.request.user
        data = self.request.data
        
        pitch_id = data.get("pitch")
        post_id = data.get("investor_post")

        if pitch_id:
            # Investor contacting Developer
            pitch = get_object_or_404(Pitch, id=pitch_id)
            serializer.save(
                investor=user,
                developer=pitch.developer,
                pitch=pitch
            )
        elif post_id:
            # Developer contacting Investor
            post = get_object_or_404(InvestorPost, id=post_id)
            serializer.save(
                developer=user,
                investor=post.investor,
                investor_post=post
            )
        else:
            # Should not happen if validation is good, but just in case
            raise ValueError("Must provide either pitch or investor_post")

    @action(detail=True, methods=["post"])
    def mark_viewed(self, request, pk=None):
        contact_request = self.get_object()
        # Only the receiver should be able to mark as viewed
        # But for simplicity, let's just allow it if they are part of the request
        contact_request.viewed = True
        contact_request.save()
        return Response({"status": "marked as viewed"})
    
    @action(detail=True, methods=["post"])
    def start_meeting(self, request, pk=None):
        """Start a scheduled meeting"""
        contact_request = self.get_object()
        user = request.user
        
        # Verify user is part of the meeting
        if user != contact_request.developer and user != contact_request.investor:
            return Response(
                {"error": "You are not authorized to start this meeting"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if meeting is scheduled
        if not contact_request.meeting_link:
            return Response(
                {"error": "No meeting link found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if meeting is within scheduled time window
        now = timezone.now()
        if contact_request.scheduled_start_time and now < contact_request.scheduled_start_time:
            return Response(
                {"error": "Meeting has not started yet"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if contact_request.scheduled_end_time and now > contact_request.scheduled_end_time:
            return Response(
                {"error": "Meeting time window has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update meeting status
        contact_request.meeting_status = 'in_progress'
        contact_request.meeting_started_at = now
        contact_request.save()
        
        return Response({
            "status": "meeting started",
            "meeting_link": contact_request.meeting_link,
            "started_at": contact_request.meeting_started_at
        })
    
    @action(detail=True, methods=["post"])
    def end_meeting(self, request, pk=None):
        """End an in-progress meeting"""
        contact_request = self.get_object()
        user = request.user
        
        # Verify user is part of the meeting
        if user != contact_request.developer and user != contact_request.investor:
            return Response(
                {"error": "You are not authorized to end this meeting"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if meeting is in progress
        if contact_request.meeting_status != 'in_progress':
            return Response(
                {"error": "Meeting is not in progress"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update meeting status
        contact_request.meeting_status = 'completed'
        contact_request.meeting_ended_at = timezone.now()
        contact_request.save()
        
        return Response({
            "status": "meeting ended",
            "ended_at": contact_request.meeting_ended_at
        })
    
    @action(detail=True, methods=["post"])
    def generate_summary(self, request, pk=None):
        """Generate a meeting summary (placeholder - can be enhanced with AI)"""
        contact_request = self.get_object()
        user = request.user
        
        # Verify user is part of the meeting
        if user != contact_request.developer and user != contact_request.investor:
            return Response(
                {"error": "You are not authorized to generate summary for this meeting"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if meeting is completed
        if contact_request.meeting_status != 'completed':
            return Response(
                {"error": "Meeting must be completed before generating summary"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate a basic summary (can be enhanced with AI transcription)
        summary_text = request.data.get('summary', '')
        
        if not summary_text:
            # Generate a default summary if none provided
            other_user = contact_request.investor if user == contact_request.developer else contact_request.developer
            context_title = contact_request.pitch.title if contact_request.pitch else contact_request.investor_post.title
            
            summary_text = f"""Meeting Summary

Participants:
- {user.first_name} {user.last_name} ({user.email})
- {other_user.first_name} {other_user.last_name} ({other_user.email})

Context: {context_title}

Meeting Duration:
- Started: {contact_request.meeting_started_at.strftime('%Y-%m-%d %H:%M:%S') if contact_request.meeting_started_at else 'N/A'}
- Ended: {contact_request.meeting_ended_at.strftime('%Y-%m-%d %H:%M:%S') if contact_request.meeting_ended_at else 'N/A'}

Summary:
[Meeting summary will be generated here. This can be enhanced with AI transcription services to automatically generate summaries from meeting recordings.]

Next Steps:
[Action items and follow-ups discussed during the meeting]
"""
        
        contact_request.meeting_summary = summary_text
        contact_request.save()
        
        return Response({
            "status": "summary generated",
            "summary": summary_text
        })
    
    @action(detail=True, methods=["get"])
    def download_summary_pdf(self, request, pk=None):
        """Download meeting summary as PDF"""
        contact_request = self.get_object()
        user = request.user
        
        # Verify user is part of the meeting
        if user != contact_request.developer and user != contact_request.investor:
            return Response(
                {"error": "You are not authorized to download this summary"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if summary exists
        if not contact_request.meeting_summary:
            return Response(
                {"error": "No summary available. Please generate a summary first."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create PDF
        response = HttpResponse(content_type='application/pdf')
        filename = f"meeting_summary_{contact_request.id}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        # Create PDF document
        doc = SimpleDocTemplate(response, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#EA580C'),
            spaceAfter=30,
        )
        story.append(Paragraph("Meeting Summary", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Participants
        other_user = contact_request.investor if user == contact_request.developer else contact_request.developer
        context_title = contact_request.pitch.title if contact_request.pitch else contact_request.investor_post.title
        
        story.append(Paragraph("<b>Participants:</b>", styles['Heading2']))
        story.append(Paragraph(f"• {user.first_name} {user.last_name} ({user.email})", styles['Normal']))
        story.append(Paragraph(f"• {other_user.first_name} {other_user.last_name} ({other_user.email})", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Context
        story.append(Paragraph("<b>Context:</b>", styles['Heading2']))
        story.append(Paragraph(context_title, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Meeting Details
        story.append(Paragraph("<b>Meeting Details:</b>", styles['Heading2']))
        meeting_data = [
            ['Scheduled Start:', contact_request.scheduled_start_time.strftime('%Y-%m-%d %H:%M:%S') if contact_request.scheduled_start_time else 'N/A'],
            ['Scheduled End:', contact_request.scheduled_end_time.strftime('%Y-%m-%d %H:%M:%S') if contact_request.scheduled_end_time else 'N/A'],
            ['Actual Start:', contact_request.meeting_started_at.strftime('%Y-%m-%d %H:%M:%S') if contact_request.meeting_started_at else 'N/A'],
            ['Actual End:', contact_request.meeting_ended_at.strftime('%Y-%m-%d %H:%M:%S') if contact_request.meeting_ended_at else 'N/A'],
            ['Status:', contact_request.get_meeting_status_display()],
        ]
        table = Table(meeting_data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph("<b>Summary:</b>", styles['Heading2']))
        # Split summary into paragraphs and add them
        summary_paragraphs = contact_request.meeting_summary.split('\n')
        for para in summary_paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip().replace('\n', '<br/>'), styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
        
        # Build PDF
        doc.build(story)
        
        return response
