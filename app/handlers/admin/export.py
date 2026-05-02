from pathlib import Path

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

from app.keyboards.admin_reply import export_keyboard
from app.services.excel_service import ExcelService
from app.states.admin_states import AdminExportStates
from app.utils.date_utils import parse_uz_date, today

router = Router(name="admin_export")


@router.message(F.text == "Bugungi ro'yxat")
async def export_today(message: Message, excel_service: ExcelService) -> None:
    await send_excel(message, await excel_service.export_users(day=today()))


@router.message(F.text == "Barcha so'rovnomadan o'tganlar")
async def export_completed(message: Message, excel_service: ExcelService) -> None:
    await send_excel(message, await excel_service.export_users(completed_only=True))


@router.message(F.text == "Sana bo'yicha")
async def export_by_date(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminExportStates.custom_date)
    await message.answer("Eksport sanasini kiriting. Format: 01.05.2026")


@router.message(AdminExportStates.custom_date, F.text)
async def export_by_date_finish(message: Message, state: FSMContext, excel_service: ExcelService) -> None:
    day = parse_uz_date(message.text)
    if day is None:
        await message.answer("Sana formati noto'g'ri. Masalan: 01.05.2026")
        return
    await state.clear()
    await send_excel(message, await excel_service.export_users(day=day))


async def send_excel(message: Message, path: Path) -> None:
    try:
        await message.answer_document(FSInputFile(path), caption="Excel fayl tayyor.")
    finally:
        path.unlink(missing_ok=True)
